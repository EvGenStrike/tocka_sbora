from storages.backends.s3boto3 import S3Boto3Storage


class ClientDocsStorage(S3Boto3Storage):
    bucket_name = 'tochka-sbora-bucket'
    file_overwrite = False