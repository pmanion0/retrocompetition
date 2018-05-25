import argparse

def CNNArgumentParser():
    ''' Create a command line argument parser for the cnn_main.py '''
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest='mode')
    subparser.required = True

    # Add BUILD only arguments
    build = subparser.add_parser('build',
                        help='build the model using the provided configuration')
    build.add_argument('-o', '--output_model_file', default=None,
                        help='file to store the trained model outputs')
    build.add_argument('-e', '--epsilon', default=0.10, type=float,
                        help='probability of taking a random action at each step')
    build.add_argument('-g', '--gamma', default=0.99, type=float,
                        help='discount rate of rewards in future time steps')
    build.add_argument('-r', '--right_bias', default=0, type=float,
                        help='amount to increase initial bias term on running right')
    build.add_argument('-s', '--model_save_interval', default=1e4, type=int,
                        help='steps between overwriting model saves')
    build.add_argument('-f', '--forecast_update_interval', default=1e3, type=int,
                        help='steps between update the Q-value future forecast model')

    # Add VALIDATE only arguments
    validate = subparser.add_parser('validate',
                        help='validate the model on a set of validation levels')

    # Add TEST only arguments
    test = subparser.add_parser('test',
                        help='WARNING: NOT YET IMPLEMENTED')

    # Add common arguments to all sub-parsers
    for p in [build, validate, test]:
        p.add_argument('-v', '--environment', choices=['aws','local','remote'], default='local',
                        help='environment script is running on to match display')
        p.add_argument('-f', '--log_folder', default='.', required=True,
                        help='folder used to store all non-model outputs')
        p.add_argument('-t', '--tracking', action='store_true',
                        help='turn on tracking outputs')
        p.add_argument('-c', '--max_step_count', default=100000, type=int,
                        help='maximum number of steps to train before terminating')
        p.add_argument('-m', '--load_model_file', default=None,
                        help='file to load starting model parameters from')

    return parser
