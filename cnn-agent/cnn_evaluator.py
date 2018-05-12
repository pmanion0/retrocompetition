import imageio
import io
import numpy as np

from matplotlib import pyplot as plt
from collections import deque
from tempfile import TemporaryDirectory

class RetroEvaluator:

    def __init__(self, log_folder, queue_memory = 100):
        self.counter = 0
        self.log_folder = log_folder
        self.memory = deque([], queue_memory)

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

    def get_memory_index(self, counter_index):
        ''' '''
        memory_index = self.counter - counter_index

        if memory_index < 0:
            raise ValueError('Desired index is in the future!')
        elif memory_index > len(self.memory):
            raise ValueError('Desired index is too far in the past ' +
                '(outside memory size)!')
        else:
            return memory_index

    def create_video(self, counter_index, pre_frames=3, post_frames=0, output_file = 'output.gif'):
        ''' Create a GIF '''
        try:
            start = counter_index - pre_frames
            end = counter_index + post_frames

            fig_array_list = []
            for m in range(start, end):
                fig = self.draw_screen_q_figure_by_index(counter_index = m)

                buf = io.BytesIO()
                fig.savefig(buf, format='png')
                plt.close(fig)
                buf.seek(0)
                f_array = imageio.imread(buf, format='png')

                fig_array_list.append(f_array)

            imageio.mimsave(self.log_folder + output_file, fig_array_list,
                format='GIF',duration = 0.5)

        except ValueError:
            print("Unable to process video")

    def format_image_tensor(self, image_tensor):
        ''' Convert PyTorch Tensor into a NumPy image for ImageIO '''
        numpy_image = image_tensor.squeeze(0).permute(1,2,0).numpy()
        return numpy_image.astype('uint8')

    def format_q_tensor(self, q_tensor):
        ''' Convert Q-estimate tensor into a NumpyArray, arranged for plotting,
            that has movement without A (jump) on top and movement with A on
            bottom '''
        q_array = q_tensor.detach().numpy()[0,:]

        out_no_A = q_array[::2].reshape(3,3)
        out_with_a = q_array[1::2].reshape(3,3)

        out_stacked = np.concatenate([out_no_A, out_with_a], axis=0)
        return out_stacked

    def output_tracking_image(self, counter_index = None, filename = None):
        ''' Output the tracking image for the given index to a file or screen '''
        if counter_index == None:
            counter_index = self.counter
        if filename == None:
            filename = 'img_{}.png'.format(counter_index)

        fig = self.draw_screen_q_figure_by_index(counter_index)

        fig.savefig(self.log_folder + filename)
        plt.close(fig)

    def draw_screen_q_figure_by_index(self, counter_index):
        ''' Draw '''
        mem_index = self.get_memory_index(counter_index)

        m = self.memory[mem_index]
        screen_array = self.format_image_tensor(m['screen'])
        q_array = self.format_q_tensor(m['Q_estimate'])

        fig = self.draw_screen_q_figure(screen_array, q_array)

        return fig


    def draw_screen_q_figure(self, screen_array, q_array):
        ''' Draw screen and Q-estimates on a single image to output to filename '''
        col_labels = ['◄','','►']
        row_labels = ['▲','', '▼']*2

        fig, ax = plt.subplots(figsize=(11,6), nrows=1, ncols=2,
            gridspec_kw = {'width_ratios':[3, 1]})
        sonic_img, q_img = ax

        sonic_img.imshow(screen_array, cmap='jet')
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
        return fig
