from regtech_data_validator.service import service_validate


def lambda_handler(event, context):

    bucket = event['Records'][0]['s3']['bucket']['name']
    file = event['Records'][0]['s3']['object']['key']
    service_validate(bucket, file)
