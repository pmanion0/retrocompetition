import boto3
import io
import torch
import csv

class RetroS3Client:

    def __init__(self, bucket = 'retro-competition-8bitbandit',
                        root_dir = 'model_outputs/'):
        self.s3_client = boto3.client('s3')
        self.bucket = bucket
        self.root_dir = root_dir
        if self.root_dir[-1] != '/': # Add trailling / if not present
            self.root_dir += '/'

    def save_buffer(self, buffer, file_name):
        ''' Save a buffer onto S3 with the given file name '''
        buffer.seek(0)
        self.s3_client.put_object(
            Body = buffer,
            Bucket = self.bucket,
            Key = self.root_dir + file_name)

    def save_memory(self, list_of_dicts, file_name):
        ''' Store a memory (list of dictionaries) directly onto S3 '''
        with io.StringIO() as str_buffer:
            dw = csv.DictWriter(str_buffer, list_of_dicts[0].keys())
            dw.writerows(list_of_dicts)
            self.s3_client.put_object(
                Body = str_buffer.getvalue().encode('utf-8'),
                Bucket = self.bucket,
                Key = self.root_dir + file_name)

    def save_model(self, model, config, file_name):
        ''' Store a (model, config) pair directly onto S3 '''
        with io.BytesIO() as buffer:
            torch.save({
                'model': self.input_to_buffer(model),
                'config': self.input_to_buffer(config)
            }, buffer)
            self.save_buffer(buffer, file_name)


    def load_to_buffer(self, model_name):
        ''' Load model off S3 into a buffer '''
        response = self.s3_client.get_object(
            Bucket = self.bucket,
            Key = self.root_dir + model_name)

        buffer = io.BytesIO(initial_bytes = response['Body'].read())
        buffer.seek(0)
        return buffer

    def input_to_buffer(self, input):
        ''' Save the input into a buffer using its .save() method '''
        buffer = io.BytesIO()
        input.save(buffer)
        buffer.seek(0)
        return buffer

    def load_model_config_buffer(self, model_name):
        ''' Load a (model, config) pair off S3 '''
        buffer = self.load_to_buffer(model_name)
        loaded_dict = torch.load(buffer)

        model_buffer = loaded_dict['model']
        config_buffer = loaded_dict['config']
        model_buffer.seek(0)
        config_buffer.seek(0)

        return model_buffer, config_buffer
