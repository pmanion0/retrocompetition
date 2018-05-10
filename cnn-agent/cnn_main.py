import sys
import os
import torch
import retro_utils as util
import torch.optim as optim
import torch.nn.functional as F

from torch import nn
from torch.autograd import Variable

from cnn_model import BasicConvolutionNetwork
from cnn_config import CNNConfig
from cnn_evaluator import RetroEvaluator

def main():
    is_local = util.parse_local(sys.argv)
    is_aws = util.parse_aws(sys.argv)

    # Initialize and load the model to train
    model = BasicConvolutionNetwork(epsilon = 0.10)
    evaluator = RetroEvaluator(log_folder = None)
    config = CNNConfig(gamma = 0.99,
        loss_func = F.smooth_l1_loss,
        opt_func = optim.RMSprop)

    #model.load_model('../../test.model')
    config.init_optimizer(model.parameters())

    # Create forecast model for future rewards
    forecast_model = util.clone_checkpoint_nn(model)

    # Create the game environment
    env = util.get_environment(is_local)

    # Reset the game and get the initial screen
    obs = env.reset()
    current_screen = util.get_screen_variable(obs)

    while evaluator.get_count() < 100000:
        # Get the Q value for the current screen
        Q_estimated = model.forward(current_screen)

        # Determine the optimal buttons to press
        buttons = model.get_buttons(Q_estimated)

        # Apply the button presses and observe the results
        obs, rew, done, info = env.step(buttons)
        next_screen = util.get_screen_variable(obs)

        Q_future = forecast_model.forward(next_screen)

        # Calculate the loss
        loss = config.calculate_loss(Q_estimated, rew, Q_future)

        # Run the gradients
        config.optimizer.zero_grad()
        loss.backward()
        config.optimizer.step()

        if evaluator.get_count() % 1000 == 0:
            forecast_model = util.clone_checkpoint_nn(model)
        if is_local and not is_aws:
            env.render()
        if done:
            obs = env.reset()

        evaluator.summarize_step(Q_estimated, buttons, rew, loss, Q_future, next_screen)
        current_screen = next_screen

    out_path = os.path.expanduser('~/test.model')
    model.save_model(out_path)


if __name__ == '__main__':
    main()
