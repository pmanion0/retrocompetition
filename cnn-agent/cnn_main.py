import sys
import os
import argparse
import torch
import retro_utils as util
import torch.optim as optim
import torch.nn.functional as F

from warnings import warn
from torch import nn
from torch.autograd import Variable
from retro_s3 import RetroS3Client

from cnn_model import BasicConvolutionNetwork
from cnn_config import CNNConfig
from cnn_evaluator import RetroEvaluator
from cnn_argparser import CNNArgumentParser

parser = CNNArgumentParser()
# sys.argv.extend(['build', '-l', 'test_ipy'])
args = parser.parse_args()

def main():
    s3 = RetroS3Client()
    model = None
    config = None

    if args.mode in ['validate','test'] and args.load_model_file == None:
        warn("Running " + args.mode + " mode without loading existing model")

    if args.load_model_file == None:
        # Define all the model and config parameters needed for training
        config = CNNConfig(
            gamma = args.gamma,
            loss_func = F.smooth_l1_loss,
            opt_func = optim.SGD,
            forecast_update_interval = args.forecast_update_interval,
            model_save_interval = args.model_save_interval
        )
        model = BasicConvolutionNetwork(
            epsilon = args.epsilon,
            right_bias = args.right_bias,
            image_to_grayscale = args.image_to_grayscale,
            image_dimension = args.image_dimension
        )
    else:
        model = BasicConvolutionNetwork()
        config = CNNConfig()

        model_buffer, config_buffer = s3.load_model_config_buffer(args.load_model_file)
        model.load(model_buffer)
        config.load(config_buffer)

    config.init_optimizer(model.parameters())

    # Set network to eval mode and do not track gradient if not training
    if args.mode in ['validate','train']:
        model.eval()
        model.turn_off_gradients()

    evaluator = RetroEvaluator(
        log_folder = args.log_folder
    )

    game_env = util.get_environment(args.environment)

    # Reset the game and get the initial screen
    obs = game_env.reset()
    current_screen = model.convert_screen_to_input(obs)

    while evaluator.get_count() < args.max_step_count:
        # Get the Q value for the current screen
        Q_estimate = model.forward(current_screen)

        # Determine the optimal buttons to press
        action = model.get_action(Q_estimate)
        buttons = model.convert_action_to_buttons(action)

        # Apply the button presses and observe the results
        obs, reward, done, info = game_env.step(buttons)

        # Reset the screen if the game round was termianted
        if done:
            obs = game_env.reset()

        next_screen = model.convert_screen_to_input(obs)

        summary = {'Q_estimate': Q_estimate, 'action': action, 'reward': reward}

        if args.mode == 'build':
            # Periodically create or update a forecast model for future rewards
            if config.is_forecast_update(evaluator.get_count()):
                forecast_model = util.clone_checkpoint_nn(model)

            # Estimate the future Q-value options
            if done:
                Q_future = torch.zeros_like(Q_estimate)
            else:
                Q_future = forecast_model.forward(next_screen)

            # Calculate the loss and create a mask identifying the action taken
            loss = config.calculate_loss(Q_estimate, reward, Q_future)
            action_mask = torch.zeros_like(loss)
            action_mask[0, action] = 1

            # Run gradient only for chosen action - zero all others with mask
            config.optimizer.zero_grad()
            loss.backward(action_mask)
            config.optimizer.step()

            summary.update({'loss': loss, 'Q_future': Q_future})

            if config.is_model_save(evaluator.get_count()) and args.output_model_file != None:
                out_path = os.path.expanduser(args.log_folder + '/' + args.output_model_file)
                s3.save_model(model, config, out_path)

        # Add all added summary information to the evaluator
        evaluator.summarize_step(**summary)

        if args.environment == 'local':
            game_env.render()

        current_screen = next_screen


if __name__ == '__main__':
    main()
