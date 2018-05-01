import torch
import io
import numpy as np

from random import random, randint
from torch import nn

class BasicConvolutionNetwork(nn.Module):

    def __init__(self, epsilon=0.05):
        ''' Screen (D,H,W): 3x224x320
            Buttons: [B, A, MODE, START, UP, DOWN, LEFT, RIGHT, C, Y, X, Z]
            Actions: [UP, DOWN, LEFT, RIGHT, (UP,LEFT), (UP,RIGHT), (DOWN,LEFT),
                      (DOWN,RIGHT), A, B, C, X, Y, Z, (A,B), (B,C), (A,X),
                      (B,Y), (C,Z), (X,Y), (Y,Z)]
            '''
        super(BasicConvolutionNetwork, self).__init__()

        self.epsilon = epsilon
        self.s3_client = None
        self.action_count = 12

        self.action_index_to_buttom_map = {
            0: ["UP"],
            1: ["DOWN"],
            2: ["LEFT"],
            3: ["RIGHT"],
            4: ["UP","LEFT"],
            5: ["UP","RIGHT"],
            6: ["DOWN","LEFT"],
            7: ["DOWN","RIGHT"],
        }

        self.button_index_list = ["B", "A", "MODE", "START", "UP", "DOWN",
            "LEFT", "RIGHT", "C", "Y", "X", "Z"]

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


    def forward(self, x):
        out = self.conv_layer(x)
        out = out.view(out.size(0), -1)
        out = self.fc_layer(out)
        return out

    def get_action(self, q_values):
        """ Return an epsilon-greedy optimal policy given the Q values """
        if random() < self.epsilon:
            action = self.get_random_action()
        else:
            action = self.get_best_q_action(q_values)
        return action

    def get_random_action(self):
        """ Return an action array with a single random action """
        action = np.array([0] * self.action_count)
        random_index = randint(0, self.action_count-1)
        action[random_index] = 1
        return action

    def get_best_q_action(self, q_values):
        """ Return an action array with the high Q-value action chosen """
        output = np.array([0] * self.action_count)

        action_index = int(q_values.max(1)[1])
        buttons = []
        if action_index > 7:
            buttons += ["A"]
            action_index -= 7
        buttons += self.action_index_to_buttom_map[action_index]

        for b in buttons:
            output[self.button_index_list.index(b)] = 1

        return output

    def action_array_to_string(self, action_array):
        ''' TODO: '''
        return ' + '.join([
            self.button_index_list[index]
            for index, value in enumerate(action_array)
            if value == 1
        ])

    def save_model(self, path):
        torch.save({
            'model': self.state_dict(),
            'epsilon': self.epsilon
        }, path)

    def load_model(self, path):
        loaded_dict = torch.load(path)
        self.epsilon = loaded_dict['epsilon']
        self.load_state_dict(loaded_dict['model'])

    def init_s3_client(self):
        if self.s3_client != None:
            pass
        import boto3
        self.s3_client = boto3.client('s3')

    def save_model_s3(self, model_name):
        ''' Store model directly onto S3 '''
        buffer = io.BytesIO()
        self.save_model(buffer)

        self.init_s3_client()
        self.s3_client.put_object(
            Body = buffer,
            Bucket = 'retro-competition-8bitbandit',
            Key = 'model_outputs/' + model_name)


    def load_model_s3(self, model_name):
        ''' Load model directly off S3 '''
        self.init_s3_client()
        response = self.s3_client.put_object(
            Bucket = 'retro-competition-8bitbandit',
            Key = 'model_outputs/' + model_name)

        buffer = io.BytesIO(initial_bytes = response['Body'].read())
        self.load_model(buffer)
