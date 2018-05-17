import boto3
import io
import torch

class RetroS3Client:

    def __init__(self, bucket = 'retro-competition-8bitbandit',
                        root_dir = 'model_outputs/'):
        self.bucket = bucket
        self.root_dir = root_dir
        self.s3_client = boto3.client('s3')

    def save_from_buffer(self, buffer, file_name):
        ''' Save a buffer onto S3 with the given file name '''
        self.s3_client.put_object(
            Body = buffer,
            Bucket = self.bucket,
            Key = self.root_dir + file_name)

    def load_to_buffer(self, model_name):
        ''' Load model off S3 into a buffer '''
        response = self.s3_client.get_object(
            Bucket = self.bucket,
            Key = self.root_dir + model_name)

        buffer = io.BytesIO(initial_bytes = response['Body'].read())
        return buffer

    def load_model_config_buffer(self, model_name):
        ''' Load a (model, config) pair off S3 '''
        buffer = self.load_to_buffer(model_name)
        loaded_dict = torch.load(buffer)
        return loaded_dict['model'], loaded_dict['config']

    def save_model(self, model, config, model_name):
        ''' Store a (model, config) pair directly onto S3 '''
        buffer = io.BytesIO()
        torch.save({
            'model': self.input_to_buffer(model),
            'config': self.input_to_buffer(config)
        }, buffer)
        self.save_from_buffer(buffer, model_name)

    def input_to_buffer(self, input):
        ''' Save the input into a buffer using its .save() method '''
        buffer = io.BytesIO()
        input.save(buffer)
        return buffer
