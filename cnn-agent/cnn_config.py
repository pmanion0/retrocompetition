from torch.autograd import Variable

class CNNConfig:
    def __init__(self, gamma, loss_func, opt_func, forecast_update_interval):
        self.gamma = gamma
        self.loss_func = loss_func
        self.opt_func = opt_func
        self.forecast_update_interval = forecast_update_interval
        self.lr = 1e-8
        self.momentum = 0.9

    def calculate_loss(self, Q_estimated, actual_reward, Q_future):
        ''' Calculate the loss to return to the network '''
        Q_observed = actual_reward + self.gamma * Q_future
        Q_observed = Variable(Q_observed.data)
        return self.loss_func(Q_estimated, Q_observed, reduce=False)

    def init_optimizer(self, params):
        self.optimizer = self.opt_func(
            params, lr = self.lr,
            momentum = self.momentum
        )

    def is_forecast_update(self, count):
        return count % self.forecast_update_interval == 0
