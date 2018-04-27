import sys
import torch
import contest_utils as util
import torch.optim as optim
import torch.nn.functional as F

from torch import nn
from torch.autograd import Variable
from cnn_model import BasicConvolutionNetwork

gamma = 0.9


def main():
    cntr = 0
    is_local = util.parse_local(sys.argv)

    # Initialize the basic training and checkpoint model
    model = BasicConvolutionNetwork()
    checkpoint_model = util.clone_checkpoint_nn(model)

    optimizer = optim.RMSprop(model.parameters())

    # Create the game environment
    env = util.get_environment(is_local)

    # Reset the game and get the initial screen
    obs = env.reset()
    screen = util.get_screen_variable(obs)

    while cntr < 10000:
        cntr += 1

        # Get the Q value for the current screen
        Q_estimated = model.forward(screen)

        # Determine the optimal action to pursue
        action = model.get_action(Q_estimated)

        # Apply the action and observe the results
        obs, rew, done, info = env.step(action)

        # Get the next screen and actual Q value
        screen = util.get_screen_variable(obs)
        Q_observed = rew + gamma * checkpoint_model.forward(screen)
        Q_observed = Variable(Q_observed.data)

        #
        loss = F.smooth_l1_loss(Q_estimated, Q_observed)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        #model.backward(Q_observed - Q_estimated)

        if cntr % 1000:
            checkpoint_model = util.clone_checkpoint_nn(model)
        if is_local:
            env.render()
        if done:
            obs = env.reset()


if __name__ == '__main__':
    main()
