import random
import torch
import numpy as np

from collections import deque

class UniformReplayMemory:

    def __init__(self, batch_size = 16, memory_size = 1e6):
        self.batch_size = batch_size
        self.memory_size = memory_size
        self.memory = deque([], memory_size)
        self.last_batch = None

    def add_memory(self, start_state, action, reward, end_state):
        ''' Add a new complete (s,a,r,s') memory for future replay

        Args:
            start_state (tensor): initial state where an action needed to be
                decided, must be a single-screen-tensor [color,width,height]
            action (int): index of the action that was taken
            reward (float): reward resulting from the action
            end_state (tensor): resulting state after the action was applied,
                must be a single-screen-tensor [color,width,height]
        '''
        self.memory.append((start_state, action, reward, end_state))

    def sample_new_batch(self):
        ''' Pull a fresh batch sample (or leave as None if memory empty) '''
        actual_batch_size = min(self.batch_size, len(self.memory))
        if actual_batch_size > 0:
            self.last_batch = random.sample(self.memory, actual_batch_size)

    def get_batch_start_including(self, last_start = None):
        ''' Return the sample of start_states with the latest start in index 0

        Args:
            last_start (tensor, optional): includes an extra start state
                `last_start`, must be a single-screen-tensor [color,width,height]

        Returns:
            a batch of starting screen-tensors [batch,color,width,height] sampled
            from replay memory plus an optional `last_start` screen-tensor
        '''
        start_states_list = [] if last_start is None else [last_start]

        if self.last_batch != None:
            start_states_list += [start for start,*_ in self.last_batch]

        start_states_tensor = torch.stack(start_states_list)
        return start_states_tensor

    def get_batch_post_action_including(self, last_action = None,
                                    last_reward = None, last_end_state = None):
        ''' Returns a sample of start_states with the latest start in index 0

        Args:
            last_action (int, optional): index of the latest action taken
            last_reward (float, optional): latest reward resulting from the
                `last_action` taken
            last_end_state (tensor, optional): latest end state after an action
                was applied, must be a single-screen-tensor [color,width,height]

        Returns:
            tuple of replay-sampled tensors of actions [batch], rewards [batch],
            and resulting screen states [batch,color,width,height]
        '''
        actions = [] if last_action is None else [last_action]
        rewards = [] if last_reward is None else [last_reward]
        end_states = [] if last_end_state is None else [last_end_state]

        if self.last_batch != None:
            unzip_batch = list(zip(*self.last_batch))
            actions += unzip_batch[1]
            rewards += unzip_batch[2]
            end_states += unzip_batch[3]

        return torch.LongTensor(actions), torch.FloatTensor(rewards), torch.stack(end_states)
