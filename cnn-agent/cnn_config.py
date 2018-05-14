from torch.autograd import Variable

class CNNConfig:
    def __init__(self, gamma, loss_func, opt_func):
        self.gamma = gamma
        self.loss_func = loss_func
        self.opt_func = opt_func

    def calculate_loss(self, Q_estimated, actual_reward, Q_future):
        ''' Calculate the loss to return to the network '''
        Q_observed = actual_reward + self.gamma * Q_future
        Q_observed = Variable(Q_observed.data)
        return self.loss_func(Q_estimated, Q_observed, reduce=False)

    def init_optimizer(self, params):
        self.optimizer = self.opt_func(params)
