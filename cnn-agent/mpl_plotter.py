import imageio
import imageio
import io

import numpy as np
from matplotlib import pyplot as plt


class MPLPlotter:

    def __init_(self):
        pass

    def output_tracking_image(self, counter_index = None, filename = None):
        ''' Output the tracking image for the given index to a file or screen '''
        if counter_index == None:
            counter_index = self.counter
        if filename == None:
            filename = 'img_{}.png'.format(counter_index)

        fig = self.draw_diagnostic_figure_by_index(counter_index)

        fig.savefig(self.log_folder + filename)
        plt.close(fig)

    def draw_diagnostic_figure_by_index(self, counter_index):
        ''' Draw the diagnostic figure using a timestep counter index '''
        mem_index = self.get_memory_index(counter_index)

        m = self.memory[mem_index]
        screen_array = self.format_image_tensor(m['screen'])
        q_array = self.format_q_tensor(m['Q_estimate'])

        fig = self.draw_diagnostic_figure(screen_array, q_array)

        return fig

    def create_video(self, counter_index, pre_frames=3, post_frames=0, output_file = 'output.gif'):
        ''' Create a GIF of frames around the desire timestep counter index '''
        try:
            start = counter_index - pre_frames
            end = counter_index + post_frames

            fig_array_list = []
            for m in range(start, end):
                fig = self.draw_diagnostic_figure_by_index(counter_index = m)

                buf = io.BytesIO()
                fig.savefig(buf, format='png')
                plt.close(fig)
                buf.seek(0)
                f_array = imageio.imread(buf, format='png')

                fig_array_list.append(f_array)

            imageio.mimsave(self.log_folder + output_file, fig_array_list,
                format='GIF',duration = 0.1)
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

    def draw_diagnostic_figure(self, screen_array, q_array):
        ''' Draw the actual diagnostic figure using the raw inputs '''
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
