import redis
import retro_s3

from collections import deque
from time import time

class RetroEvaluator:

    def __init__(self,
                log_folder,
                log_system = 'redis',
                min_write_gap = 30,
                queue_memory = 100,
                print_log_messages = True,
                redis_host = 'model-storage.bkgf6l.0001.use1.cache.amazonaws.com',
                redis_port = 6379):
        self.counter = 0
        self.write_number = 0
        self.last_write_time = time()

        self.log_system = log_system
        self.print_log_messages = print_log_messages
        self.min_write_gap = min_write_gap
        self.common_memory = deque([], queue_memory)
        self.selective_memory = deque([], queue_memory)
        self.log_folder = log_folder

        if log_system == 's3':
            self.s3 = retro_s3.RetroS3Client()
        elif log_system == 'redis':
            self.redis = redis.StrictRedis(host=redis_host, port=redis_port)
            self.redis_pipeline = self.redis.pipeline()
            self.redis.rpush('model_names', self.log_folder)
        else:
            pass #self.log_system = open('')

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

    def write_metrics_s3(self, metric_type):
        ''' Write either the common or selective metrics to S3 '''
        dir = self.log_folder
        num = self.write_number

        if metric_type == 'common':
            self.s3.save_memory(self.common_memory,
                f"{dir}/common_metrics/{num:010}.csv")
        elif metric_type == 'selective':
            self.s3.save_memory(self.selective_memory,
                f"{dir}/select_metrics/{num:010}.csv")

    def write_metrics_redis(self, metric_type):
        ''' '''
        name = self.log_folder
        pipe = self.redis_pipeline

        if metric_type == 'common':
            for m in self.common_memory:
                pipe.rpush(name + ':action', m['action'])
                pipe.rpush(name + ':reward', m['reward'])
                pipe.rpush(name + ':loss', m['loss'])
        elif metric_type == 'selective':
            for m in self.selective_memory:
                pipe.rpush(name + ':q_estimate', m['Q_estimate'][0])
                # TODO: Finish selective memory approach
        pipe.incrby(name + ':count', len(self.common_memory))
        pipe.execute()

    def write_metrics(self):
        ''' Write out the latest memory and update last write time '''
        self.write_common_memory()
        self.common_memory.clear()

        if len(self.selective_memory) > 0:
            self.write_selective_memory()
            self.selective_memory.clear()

        self.write_number += 1
        self.last_write_time = time()

    def get_count(self):
        ''' Returns the step count '''
        return self.counter
