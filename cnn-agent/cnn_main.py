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

#'../../test.model'
#'~/test.model'

parser = argparse.ArgumentParser(description="")
parser.add_argument('-e', '--epsilon', default=0.10, type=float,
                    help='probability of taking a random action at each step')
parser.add_argument('-l', '--local', action='store_true',
                    help='indicator to initialize local environment with video')
parser.add_argument('-f', '--log_folder', default='',
                    help='folder used to store all non-model outputs')
parser.add_argument('-g', '--gamma', default=0.99, type=float,
                    help='discount rate of rewards in future time steps')
parser.add_argument('-m', '--load_model_file', default=None,
                    help='file to load initial model parameters from')
parser.add_argument('-r', '--right_bias', default=0, type=float,
                    help='amount to increase initial bias term on running right')
parser.add_argument('-c', '--max_step_count', default=100000, type=int,
                    help='maximum number of steps to train before terminating')
parser.add_argument('-o', '--output_model_file', default=None,
                    help='file to store the trained model outputs')
parser.add_argument('-t', '--tracking', action='store_true',
                    help='turn on tracking outputs')

args = parser.parse_args()

def main():
    is_local = args.local
    is_aws = util.parse_aws(sys.argv)

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
    env = util.get_environment(is_local)

    # Reset the game and get the initial screen
    obs = env.reset()
    current_screen = util.get_screen_variable(obs)

    while evaluator.get_count() < args.max_step_count:
        # Get the Q value for the current screen
        Q_estimated = model.forward(current_screen)

        # Determine the optimal buttons to press
        action = model.get_action(Q_estimated)
        buttons = model.convert_action_to_buttons(action)

        # Apply the button presses and observe the results
        obs, reward, done, info = env.step(buttons)
        next_screen = util.get_screen_variable(obs)

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
        if is_local and not is_aws:
            env.render()
        if done:
            obs = env.reset()

        evaluator.summarize_step(Q_estimated, buttons, rew, loss, Q_future, next_screen)
        current_screen = next_screen

        # Output useful diagnostic figures during training (SLOW!)
        if args.tracking:
            evaluator.output_tracking_image()

    if args.output_model_file != None:
        out_path = os.path.expanduser(args.output_model_file)
        model.save_model(out_path)


if __name__ == '__main__':
    main()
