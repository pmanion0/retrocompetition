


class RetroEvaluator:

    def __init__(self, log_folder):
        self.counter = 0
        self.log_folder = log_folder
        pass

    def summarize_step(self, Q_estimated, action, reward, loss, Q_future, next_screen):
        ''' Provides evaluator the summary of the last step '''
        print("{o}: {l}".format(o=self.counter, l=loss))
        self.counter += 1
        pass

    def get_count(self):
        ''' Returns the step count '''
        return self.counter
