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
from cnn_memory import UniformReplayMemory

parser = CNNArgumentParser()
# sys.argv.extend(['build', '-l', 'test_ipy'])
args = parser.parse_args()

if not args.disable_cuda and torch.cuda.is_available():
    args.device = torch.device('cuda')
else:
    args.device = torch.device('cpu')

def main():
    s3 = RetroS3Client()
    model = None
    config = None

    if args.mode in ['validate','test'] and args.load_model_file == None:
        warn("Running " + args.mode + " mode without loading existing model")

    if args.load_model_file == None:
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

    memory = UniformReplayMemory(
        memory_size = args.memory_size,
        batch_size = args.batch_size
    )

    game_env = util.get_environment(args.environment)

    # Reset the game and get the initial screen
    obs = game_env.reset()
    current_screen = model.convert_screen_to_input(obs)

    while evaluator.get_count() < args.max_step_count:
        if args.mode == 'build' and args.use_experience_replay:
            memory.sample_new_batch()
            batch_states = memory.get_batch_start_including(current_screen)
        else:
            batch_states = current_screen.unsqueeze(0)

        # Get the Q value for the current screen
        Q_estimates = model.forward(batch_states)

        # Determine the optimal buttons to press for the current screen
        current_Q_estimate = Q_estimates[0]
        action = model.get_action(current_Q_estimate)
        buttons = model.convert_action_to_buttons(action)

        # Apply the button presses and observe the results
        obs, reward, done, info = game_env.step(buttons)

        # Reset the screen if the game round was termianted
        if done:
            obs = game_env.reset()

        next_screen = model.convert_screen_to_input(obs)

        summary = {'Q_estimate': Q_estimates[0], 'action': action, 'reward': reward}

        if args.mode == 'build':
            batch_actions, batch_rewards, batch_next_screens = \
                memory.get_batch_post_action_including(action, reward, next_screen)

            # Periodically create or update a forecast model for future rewards
            if config.is_forecast_update(evaluator.get_count()):
                forecast_model = util.clone_checkpoint_nn(model)

            # Estimate the future Q-value options
            Q_futures = forecast_model.forward(batch_next_screens)

            if done: # Set future Q-values to zero if round terminated
                Q_futures[0,:] = torch.zeros_like(Q_futures[0,:])

            # Calculate the loss and create a mask identifying the action taken
            loss = config.calculate_loss(Q_estimates, batch_rewards, Q_futures)

            action_mask = torch.zeros_like(loss)
            action_mask.scatter_(1, batch_actions.view(-1,1), 1.0)

            # Run gradient only for chosen action - zero all others with mask
            config.optimizer.zero_grad()
            loss.backward(action_mask)
            config.optimizer.step()

            memory.add_memory(current_screen, action, reward, next_screen)
            summary.update({'loss': loss[0], 'Q_future': Q_futures[0]})

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
