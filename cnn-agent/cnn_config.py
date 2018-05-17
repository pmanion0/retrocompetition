import torch

import torch.nn.functional as F
import torch.optim as optim

from torch.autograd import Variable

class CNNConfig:
    def __init__(self, gamma = 0.99, loss_func = F.smooth_l1_loss,
                 opt_func = optim.SGD, forecast_update_interval = 1e3,
                 lr = 1e-8, momentum = 0.9):
        self.gamma = gamma
        self.loss_func = loss_func
        self.opt_func = opt_func
        self.forecast_update_interval = forecast_update_interval
        self.lr = lr
        self.momentum = momentum

    def calculate_loss(self, Q_estimated, actual_reward, Q_future):
        ''' Calculate the loss to return to the network '''
        Q_observed = actual_reward + self.gamma * Q_future
        Q_observed = Variable(Q_observed.data)
        return self.loss_func(Q_estimated, Q_observed, reduce=False)

    def init_optimizer(self, params):
        self.optimizer = self.opt_func(
            params,
            lr = self.lr,
            momentum = self.momentum
        )

    def is_forecast_update(self, count):
        return count % self.forecast_update_interval == 0

    def save(self, path_or_buffer):
        ''' Save config to a local file path or buffer '''
        torch.save({
            'gamma': self.gamma,
            #'loss_func': self.loss_func,
            'opt_func': self.opt_func,
            'forecast_update_interval': self.forecast_update_interval,
            'lr': self.lr,
            'momentum': self.momentum
        }, path_or_buffer)

    def load(self, path_or_buffer):
        ''' Load config from a local file path or buffer '''
        loaded_dict = torch.load(path_or_buffer)
        self.gamma = loaded_dict['gamma']
        #self.loss_func = loaded_dict['loss_func']
        self.opt_func = loaded_dict['opt_func']
        self.forecast_update_interval = loaded_dict['forecast_update_interval']
        self.lr = loaded_dict['lr']
        self.momentum = loaded_dict['momentum']
