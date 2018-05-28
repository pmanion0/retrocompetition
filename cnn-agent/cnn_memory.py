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
        ''' Add a new complete memory for future replay '''
        self.memory.append((start_state, action, reward, end_state))

    def sample_new_batch(self):
        ''' Pull a fresh batch sample (or leave as None if memory empty) '''
        actual_batch_size = min(self.batch_size, len(self.memory))
        if actual_batch_size > 0:
            self.last_batch = random.sample(self.memory, actual_batch_size)

    def get_batch_start_including(self, last_start):
        ''' Return the sample of start_states with the latest start in index 0 '''
        start_states_list = [] if last_start is None else [last_start]

        if self.last_batch != None:
            start_states_list += [start for start,*_ in self.last_batch]

        start_states_tensor = torch.stack(start_states_list).squeeze(1)
        return start_states_tensor

    def get_batch_post_action_including(self, last_action, last_reward, last_end_state):
        ''' Return a sample of start_states with the latest start in index 0 '''
        actions = [] if last_action is None else [last_action]
        rewards = [] if last_reward is None else [last_reward]
        end_states = [] if last_end_state is None else [last_end_state]

        if self.last_batch != None:
            unzip_batch = list(zip(*self.last_batch))
            actions += unzip_batch[1]
            rewards += unzip_batch[2]
            end_states += unzip_batch[3]

        return torch.LongTensor(actions), torch.FloatTensor(rewards), torch.stack(end_states).squeeze(1)
