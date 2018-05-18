from collections import deque

class RetroEvaluator:

    def __init__(self, log_folder, queue_memory = 100):
        self.counter = 0
        self.log_folder = log_folder
        self.memory = deque([], queue_memory)
        self.metrics_file = open(self.log_folder + '/metrics.log')

    def summarize_step(self, Q_estimate = None, action = None, reward = None,
                       loss = None, Q_future = None, next_screen = None):
        ''' Provides evaluator the summary of the last step '''
        memory = {'Q_estimate': Q_estimate, 'action': action, 'reward': reward,
            'loss': loss, 'Q_future': Q_future, 'screen': next_screen}

        self.memory.appendleft(memory)
        self.counter += 1

        print("{o}: {l}".format(o=self.counter, l=loss[0,action]))

    def get_count(self):
        ''' Returns the step count '''
        return self.counter

    def get_memory_index(self, counter_index):
        ''' Convert the time-step counter index into an index for pulling
            information out of the memory queue '''
        memory_index = self.counter - counter_index

        if memory_index < 0:
            raise ValueError('Desired index is in the future!')
        elif memory_index > len(self.memory):
            raise ValueError('Desired index is too far in the past ' +
                '(outside memory size)!')
        else:
            return memory_index
