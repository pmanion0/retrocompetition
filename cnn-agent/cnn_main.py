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



def main():
    cntr = 0
    is_local = util.parse_local(sys.argv)
    is_aws = util.parse_aws(sys.argv)

    # Initialize and load the model to train
    model = BasicConvolutionNetwork()
    model.load_model('../../test.model')

    # Setup the config with other training parameters
    config = CNNConfig(gamma = 0.96,
        loss_func = F.smooth_l1_loss,
        opt_func = optim.RMSprop)

    config.init_optimizer(model.parameters())

    # Create forecast model for future rewards
    forecast_model = util.clone_checkpoint_nn(model)

    # Create the game environment
    env = util.get_environment(is_local)

    # Reset the game and get the initial screen
    obs = env.reset()
    current_screen = util.get_screen_variable(obs)

    while cntr < 100000:
        cntr += 1

        # Get the Q value for the current screen
        Q_estimated = model.forward(current_screen)

        # Determine the optimal action to pursue
        action = model.get_action(Q_estimated)

        # Apply the action and observe the results
        obs, rew, done, info = env.step(action)
        next_screen = util.get_screen_variable(obs)

        Q_future = forecast_model.forward(next_screen)

        # Calculate the loss
        loss = config.get_loss(Q_estimated, rew, Q_future)

        # Run the gradients
        config.optimizer.zero_grad()
        config.loss.backward()
        config.optimizer.step()

        print("{o}: {l}".format(o=cntr, l=loss))

        if cntr % 1000:
            forecast_model = util.clone_checkpoint_nn(model)
        if is_local and not is_aws:
            env.render()
        if done:
            obs = env.reset()

        current_screen = next_screen

    out_path = os.path.expanduser('~/test.model')
    model.save_model(out_path)


if __name__ == '__main__':
    main()
