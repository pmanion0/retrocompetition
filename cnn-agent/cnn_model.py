import torch
import io
import numpy as np

from retro_s3 import RetroS3Client
from random import random, randint
from torch import nn

class BasicConvolutionNetwork(nn.Module):

    def __init__(self, epsilon = 0.05, right_bias = 0):
        ''' Screen (D,H,W): 3x224x320
            Buttons: [B, A, MODE, START, UP, DOWN, LEFT, RIGHT, C, Y, X, Z]
            Actions: [UP, DOWN, LEFT, RIGHT, (UP,LEFT), (UP,RIGHT), (DOWN,LEFT),
                      (DOWN,RIGHT), A, B, C, X, Y, Z, (A,B), (B,C), (A,X),
                      (B,Y), (C,Z), (X,Y), (Y,Z)]
            '''
        super(BasicConvolutionNetwork, self).__init__()

        self.epsilon = epsilon
        self.s3_client = RetroS3Client()

        # Number of possible buttons (can be 0 for off, 1 for on)
        self.button_index_list = ["B", "A", "MODE", "START", "UP", "DOWN",
            "LEFT", "RIGHT", "C", "Y", "X", "Z"]

        self.button_count = len(self.button_index_list)

        # Number of unique actions to decide between (combination of buttons)
        self.action_index_to_buttom_map = {
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

        self.action_count = len(self.action_index_to_buttom_map)

        # Define neural network architecture
        self.conv_layer = nn.Sequential(
            nn.Conv2d(3, 10, 7, padding=3),
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

        # Increase bias to move rightwards
        self.fc_layer[0].bias.data[10].add_(right_bias)


    def forward(self, x):
        out = self.conv_layer(x)
        out = out.view(out.size(0), -1)
        out = self.fc_layer(out)
        return out

    def get_buttons(self, q_values):
        """ Return an epsilon-greedy optimal policy given the Q values """
        if random() < self.epsilon:
            action = self.get_random_action()
        else:
            action = self.get_best_q_action(q_values)

        button_array = self.convert_action_to_buttons(action)
        return button_array

    def convert_action_to_buttons(self, action):
        ''' Convert list of actions to press (as strings) into an array with
            each button to press to pass into simulation, e.g.
            ["UP","B"] -> [1,0,0,0,1,0,0,0,0,0,0,0] '''
        button_array = np.array([0] * self.button_count)
        for a in action:
            button_array[self.button_index_list.index(a)] = 1
        return button_array

    def get_random_action(self):
        """ Return an action array with a single random action """
        random_action_index = randint(0, self.action_count-1)
        random_action = self.action_index_to_buttom_map[random_action_index]
        return random_action

    def get_best_q_action(self, q_values):
        """ Return an action array with the high Q-value action chosen """
        best_action_index = int(q_values.max(1)[1])
        best_action = self.action_index_to_buttom_map[best_action_index]
        return best_action

    def buttons_to_string(self, button_array):
        ''' Convert array of button presses into an interpretable string '''
        return ' + '.join([
            self.button_index_list[index]
            for index, value in enumerate(button_array)
            if value == 1
        ])

    def save_model(self, path_or_buffer):
        ''' Save model to a local file path or buffer '''
        torch.save({
            'model': self.state_dict(),
            'epsilon': self.epsilon
        }, path_or_buffer)

    def load_model(self, path_or_buffer):
        ''' Load model from a local file path or buffer '''
        loaded_dict = torch.load(path_or_buffer)
        self.epsilon = loaded_dict['epsilon']
        self.load_state_dict(loaded_dict['model'])

    def save_model_s3(self, model_name):
        ''' Store model directly onto S3 '''
        buffer = io.BytesIO()
        self.save_model(buffer)
        self.s3_client.save_from_buffer(buffer, model_name)

    def load_model_s3(self, model_name):
        ''' Load model directly off S3 '''
        buffer = self.s3_client.load_to_buffer(model_name)
        self.load_model(buffer)
