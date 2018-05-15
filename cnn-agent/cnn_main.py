import sys
import os
import argparse
import torch
import retro_utils as util
import torch.optim as optim
import torch.nn.functional as F

from torch import nn
from torch.autograd import Variable

from cnn_model import BasicConvolutionNetwork
from cnn_config import CNNConfig
from cnn_evaluator import RetroEvaluator
from cnn_argparser import CNNArgumentParser

parser = CNNArgumentParser()
args = parser.parse_args()

def main():
    # Initialize and load the model to train
    model = BasicConvolutionNetwork(epsilon = args.epsilon,
        right_bias = args.right_bias)
    evaluator = RetroEvaluator(log_folder = args.log_folder)
    config = CNNConfig(gamma = args.gamma,
        loss_func = F.smooth_l1_loss,
        opt_func = optim.SGD)

    if args.load_model_file != None:
        model.load_model(args.load_model_file)
    config.init_optimizer(model.parameters())

    # Create forecast model for future rewards
    forecast_model = util.clone_checkpoint_nn(model)

    # Create the game environment
    env = util.get_environment(args.environment)

    # Reset the game and get the initial screen
    obs = env.reset()
    current_screen = model.convert_screen_to_input(obs)

    while evaluator.get_count() < args.max_step_count:
        # Get the Q value for the current screen
        Q_estimated = model.forward(current_screen)

        # Determine the optimal buttons to press
        action = model.get_action(Q_estimated)
        buttons = model.convert_action_to_buttons(action)

        # Apply the button presses and observe the results
        obs, reward, done, info = env.step(buttons)
        next_screen = model.convert_screen_to_input(obs)

        Q_future = forecast_model.forward(next_screen)

        # Calculate the loss
        loss = config.calculate_loss(Q_estimated, reward, Q_future)
        action_mask = torch.zeros_like(loss)
        action_mask[0, action] = 1

        # Run the gradient (only for chosen action -- zero all other gradients)
        config.optimizer.zero_grad()
        loss.backward(action_mask)
        config.optimizer.step()

        if evaluator.get_count() % 1000 == 0:
            forecast_model = util.clone_checkpoint_nn(model)
        if args.environment == 'local':
            env.render()
        if done:
            obs = env.reset()

        evaluator.summarize_step(Q_estimated, action, reward, loss, Q_future, next_screen)
        current_screen = next_screen

        # Output useful diagnostic figures during training (SLOW!)
        if args.tracking:
            evaluator.output_tracking_image()

    if args.output_model_file != None:
        out_path = os.path.expanduser(args.output_model_file)
        model.save_model(out_path)


if __name__ == '__main__':
    main()
