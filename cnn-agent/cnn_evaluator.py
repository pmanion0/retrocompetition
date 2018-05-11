import imageio
import numpy as np

from matplotlib import pyplot as plt
from collections import deque

class RetroEvaluator:

    def __init__(self, log_folder, queue_memory = 100):
        self.counter = 0
        self.log_folder = log_folder
        self.memory = deque([None]*queue_memory, queue_memory)

    def summarize_step(self, Q_estimate, action, reward, loss, Q_future, next_screen):
        ''' Provides evaluator the summary of the last step '''
        memory = {'Q_estimate': Q_estimate, 'action': action, 'reward': reward,
            'loss': loss, 'Q_future': Q_future, 'screen': next_screen}

        self.memory.appendleft(memory)
        self.counter += 1

        print("{o}: {l}".format(o=self.counter, l=loss))

    def get_count(self):
        ''' Returns the step count '''
        return self.counter


    def create_video(self, counter_index, pre_frames=3, post_frames=0):
        ''' Create a GIF '''
        if counter_index + post_frames > self.counter:
            pass # Have not observed sufficient post-frames
        pass

    def create_image(self, counter_index = None, filename = None):
        ''' '''
        if counter_index == None:
            counter_index = self.counter
        if filename == None:
            filename = 'img_{}.png'.format(counter_index)

        mem_index = self.counter - counter_index

        m = self.memory[mem_index]
        screen_array = self.format_image_tensor(m['screen'])
        q_array = self.format_q_tensor(m['Q_estimate'])

        self.plot_screen_q(screen_array, q_array, filename)

    def format_image_tensor(self, image_tensor):
        ''' Convert PyTorch Tensor into a NumPy image for ImageIO '''
        numpy_image = image_tensor.squeeze(0).permute(1,2,0).numpy()
        return numpy_image.astype('uint8')

    def format_q_tensor(self, q_tensor):
        q_array = q_tensor.detach().numpy()[0,:]
        out_no_A = q_array[::2].reshape(3,3)
        out_with_a = q_array[1::2].reshape(3,3)
        out_stacked = np.concatenate([out_no_A, out_with_a], axis=0)
        return out_stacked

    def plot_screen_q(self, screen_array, q_array, filename):
        col_labels = ['◄','','►']
        row_labels = ['▲','', '▼']*2

        fig, ax = plt.subplots(figsize=(11,6), nrows=1, ncols=2,
            gridspec_kw = {'width_ratios':[3, 1]})
        sonic_img, q_img = ax

        sonic_img.imshow(screen_array)
        sonic_img.set_axis_off()

        q_img.imshow(q_array)
        q_img.set_axis_off()

        for r in range(len(row_labels)):
            for c in range(len(col_labels)):
                direction_img = ''
                if r in [0, 2, 3, 5] and c in [1]:
                    direction_img = row_labels[r]
                elif r in [1, 4] and c in [0, 2]:
                    direction_img = col_labels[c]
                elif r == 4 and c == 1:
                    direction_img = "A"

                q_img.text(c, r, direction_img,
                    ha="center", va="center", color="gray", fontsize=20, alpha=0.3)
                q_img.text(c, r, "{:5.2f}".format(q_array[r,c]),
                    ha="center", va="center", color="w", fontsize=6)

        fig.tight_layout(pad=0)
        fig.savefig(self.log_folder + filename)
        plt.close(fig)
