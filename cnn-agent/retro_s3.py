import boto3
import io

class RetroS3Client:

    def __init__(self, bucket = 'retro-competition-8bitbandit',
                        root_dir = 'model_outputs/'):
        self.bucket = bucket
        self.root_dir = root_dir
        self.s3_client = boto3.client('s3')

    def save_from_buffer(self, buffer, name):
        self.s3_client.put_object(
            Body = buffer,
            Bucket = self.bucket,
            Key = self.root_dir + model_name)

    def load_to_buffer(self, model_name):
        ''' Load model off S3 into a buffer '''
        response = self.s3_client.get_object(
            Bucket = self.bucket,
            Key = self.root_dir + model_name)

        buffer = io.BytesIO(initial_bytes = response['Body'].read())
        return buffer
