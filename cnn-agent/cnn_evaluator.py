from retro_s3 import RetroS3Client
from collections import deque
from time import time

class RetroEvaluator:

    def __init__(self, log_folder, min_write_gap = 30, queue_memory = 100,
                print_log_messages = True):
        self.s3 = RetroS3Client()
        self.counter = 0
        self.write_number = 0
        self.last_write_time = time()

        self.print_log_messages = print_log_messages
        self.min_write_gap = min_write_gap
        self.common_memory = deque([], queue_memory)
        self.selective_memory = deque([], queue_memory)
        self.log_folder = log_folder

    def summarize_step(self, Q_estimate, action, reward,
                       loss = None, Q_future = None, next_screen = None):
        ''' Provides evaluator the summary of the last step

        Args:
            Q_estimate (tensor):
            action (int):
            reward (float):
            loss (tensor, optional):
            Q_future (tensor, optional):
            next_screen (tensor, optional): 
        '''
        common_memory = {
            'counter': self.counter,
            'action': action,
            'reward': reward,
            'loss': loss if type(loss) is float or loss is None else float(loss[action])
        }
        selective_memory = {
            'Q_estimate': Q_estimate,
            'Q_future': Q_future,
            'screen': next_screen
        }

        self.common_memory.append(common_memory)
        self.counter += 1

        if self.is_notable(common_memory, selective_memory):
            self.selective_memory.append(selective_memory)
        if self.is_write_time():
            self.write_metrics()
        if self.print_log_messages:
            self.print_log_message(common_memory, selective_memory)

    def print_log_message(self, common, selective):
        ''' Print logging messages to STDOUT '''
        print("{o}: {l}".format(o=common['counter'], l=common['loss']))

    def is_notable(self, common, selective):
        ''' Return whether the step was notable enough to output more advanced
            diagnostics (e.g. Q-values, screen images, etc.) '''
        return False

    def is_write_time(self):
        ''' Return whether it is time to write (either memory is full or it
            has been too much time since the last write '''
        is_memory_full = (len(self.common_memory) >= self.common_memory.maxlen)
        is_time_reached = ((time() - self.last_write_time) >= self.min_write_gap)
        return (is_memory_full or is_time_reached)

    def write_metrics(self):
        ''' Write out the latest memory and update last write time '''
        dir = self.log_folder
        num = self.write_number

        self.s3.save_memory(self.common_memory, f"{dir}/common_metrics/{num:010}.csv")
        self.common_memory.clear()

        if len(self.selective_memory) > 0:
            self.s3.save_memory(self.selective_memory, f"{dir}/select_metrics/{num:010}.csv")
            self.selective_memory.clear()

        self.write_number += 1
        self.last_write_time = time()

    def get_count(self):
        ''' Returns the step count '''
        return self.counter
