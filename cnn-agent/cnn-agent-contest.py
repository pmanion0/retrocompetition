import sys
import torch
import contest_utils as util

from torch import nn
from torch.autograd import Variable
from cnn_model import BasicConvolutionNetwork

def main():
    cntr = 0
    is_local = util.parse_local(sys.argv)

    model = BasicConvolutionNetwork()
    env = util.get_environment(is_local)

    obs = env.reset()

    while cntr < 100:
        cntr += 1
        # Get the screen and convert from (h,w,d) to (d,h,w)
        screen = Variable(torch.FloatTensor(env.render("rgb_array")))
        screen = screen.permute(2,0,1)

        output = model.forward(screen.unsqueeze(0))

        action = util.get_action(output)

        obs, rew, done, info = env.step(action)

        model.backward(rew)

        if is_local:
            env.render()
        if done:
            obs = env.reset()


if __name__ == '__main__':
    main()
