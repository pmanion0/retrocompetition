import torch
import io
import numpy as np

from random import random, randint
from torch import nn
from torch.autograd import Variable

from torchvision.transforms.functional import to_pil_image
from torchvision.transforms.functional import to_tensor


class BasicConvolutionNetwork(nn.Module):

    def __init__(self, epsilon = 0.05, right_bias = 0, image_to_grayscale = False,
                image_dimension = (100,100)):
        ''' Initialize DQN network '''
        super(BasicConvolutionNetwork, self).__init__()

        self.image_dimension = image_dimension
        self.image_to_grayscale = image_to_grayscale
        self.epsilon = epsilon
        self.right_bias = right_bias

        # Number of possible buttons (can be 0 for off, 1 for on)
        self.button_index_list = ["B", "A", "MODE", "START", "UP", "DOWN",
            "LEFT", "RIGHT", "C", "Y", "X", "Z"]

        self.button_count = len(self.button_index_list)

        # Number of unique actions to decide between (combination of buttons)
        self.action_index_to_string_map = {
            0:  ["UP","LEFT"],     1: ["A","UP","LEFT"],
            2:  ["UP"],            3: ["A","UP"],
            4:  ["UP","RIGHT"],    5: ["A","UP","RIGHT"],
            6:  ["LEFT"],          7: ["A","LEFT"],
            8:  [],                9: ["A"],
            10: ["RIGHT"],        11: ["A","RIGHT"],
            12: ["DOWN","LEFT"],  13: ["A","DOWN","LEFT"],
            14: ["DOWN"],         15: ["A","DOWN"],
            16: ["DOWN","RIGHT"], 17: ["A","DOWN","RIGHT"]
        }

        self.action_count = len(self.action_index_to_string_map)

        self.__init_network__()

    def __init_network__(self):
        ''' Create the actual neural network after basic initialization '''
        input_dimension = 1 if self.image_to_grayscale else 3

        if self.image_dimension == (320,224):
            self.conv_layer = nn.Sequential(
                nn.Conv2d(input_dimension, 10, 7, padding=3),
                nn.ReLU(),
                nn.MaxPool2d(4, stride=4), # 10x56x80
                nn.Conv2d(10, 32, 3, padding=1),  # 32x56x80
                nn.ReLU(),
                nn.MaxPool2d(4, stride=4), # 32x14x20
                nn.Conv2d(32, 64, 3, padding=1), # 64x14x20
                nn.ReLU(),
                nn.MaxPool2d(2, stride=2) # 64x7x10
            )

            self.fc_layer = nn.Sequential(
                nn.Linear(64*7*10, self.action_count)
            )
        elif self.image_dimension == (100,100):
            self.conv_layer = nn.Sequential(
                nn.Conv2d(input_dimension, 10, 6, stride=2, padding=2),
                nn.ReLU(), # 10x50x50
                nn.Conv2d(10, 32, 6, stride=2, padding=2),
                nn.ReLU(), # 32x25x25
                nn.Conv2d(32, 64, 7, stride=2, padding=2),
                nn.ReLU() # 64x12x12
            )

            self.fc_layer = nn.Sequential(
                nn.Linear(64*12*12, self.action_count)
            )
        else:
            raise ValueError("No network available for the given image_dimension")

        # Increase bias to move rightwards
        self.fc_layer[0].bias.data[10].add_(self.right_bias)

    def convert_screen_to_input(self, obs):
        ''' Convert the screen from an image into an array suitable for NN

        Args:
            NumPy array [height,width,color] where color is RGB (3 dimensions)

        Returns:
            a single-screen tensor [color, width, height] where color is either
            RGB (3 dimensions) or grayscale (1 dimension)
        '''
        pil_image = to_pil_image(obs)
        if self.image_to_grayscale:
            #obs = self.numpy_rgb_to_grayscale(obs)
            pil_image = pil_image.convert('L')
        if self.image_dimension != (320,224):
            pil_image = pil_image.resize(self.image_dimension)
        nn_input = Variable(to_tensor(pil_image))
        return nn_input

    def forward(self, x):
        out = self.conv_layer(x)
        out = out.view(out.size(0), -1)
        out = self.fc_layer(out)
        return out

    def turn_off_gradients(self):
        ''' Turns off gradient storage for this model, used for forecast models
            or during evaluation/testing of a pre-trained model '''
        for param in self.conv_layer.parameters():
            param.requires_grad = False
        for param in self.fc_layer.parameters():
            param.requires_grad = False

    def convert_action_to_buttons(self, action):
        ''' Convert list of actions to press (as strings) into an array with
            each button to press to pass into simulation, e.g.
            ["UP","B"] ->

        Args:
            action (int): index of the action to convert

        Returns:
            np.array of size count(buttons) with a 1 for each button that the
            action index implies should be pressed and 0 for all other buttons

        Example:
            >>> m.convert_action_to_buttons(1) # equals ["UP","LEFT","A"]
            np.array([0,1,0,0,1,0,1,0,0,0,0,0])
        '''
        button_array = np.array([0] * self.button_count)
        action_str = self.action_index_to_string_map[action]
        for a in action_str:
            button_array[self.button_index_list.index(a)] = 1
        return button_array

    def get_action(self, q_values):
        ''' Return an epsilon-greedy optimal policy given the Q values

        Args:
            q_values (tensor): tensor of size [count(actions)] with the
                expected Q-value that will result from taking each action

        Returns:
            int with the epsilon-greedy action index to pick
        '''
        if random() < self.epsilon:
            action = self.get_random_action()
        else:
            action = self.get_best_q_action(q_values)
        return action

    def get_random_action(self):
        ''' Return an action array with a single random action

        Returns:
            int with a random action index to take
        '''
        random_action_index = randint(0, self.action_count-1)
        return random_action_index

    def get_best_q_action(self, q_values):
        ''' Return an action array with the high Q-value action chosen

        Args:
            q_values (tensor): tensor of size [count(actions)] with the
                expected Q-value that will result from taking each action

        Returns:
            int with the best (maximal Q-value) action index to pick
        '''
        best_action_index = int(q_values.argmax(dim=0))
        return best_action_index

    def buttons_to_string(self, button_array):
        ''' Convert array of button presses into an interpretable string

        Args:
            button_array (np.array): array of size count(buttons) with 0 if the
                button is not pressed and 1 if it is pressed

        Returns:
            string showing each button pressed with ' + ' between them

        Example:
            >>> buttons = np.array([1,0,0,0,1,0,0,0,0,0,0,0])
            >>> b.buttons_to_string(buttons)
            'B + UP'
        '''
        return ' + '.join([
            self.button_index_list[index]
            for index, value in enumerate(button_array)
            if value == 1
        ])

    def save(self, path_or_buffer):
        ''' Save model to a local file path or buffer '''
        torch.save({
            'model': self.state_dict(),
            'epsilon': self.epsilon,
            'right_bias': self.right_bias,
            'image_dimension': self.image_dimension,
            'image_to_grayscale': self.image_to_grayscale
        }, path_or_buffer)

    def load(self, path_or_buffer):
        ''' Load model from a local file path or buffer '''
        loaded_dict = torch.load(path_or_buffer)
        self.epsilon = loaded_dict['epsilon']
        self.right_bias = loaded_dict['right_bias']
        self.image_dimension = loaded_dict['image_dimension']
        self.image_to_grayscale = loaded_dict['image_to_grayscale']
        self.__init_network__()
        self.load_state_dict(loaded_dict['model'])
