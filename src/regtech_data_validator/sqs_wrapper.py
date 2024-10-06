import os
import boto3
import json
import logging

from regtech_data_validator.service import service_validate

logger = logging.getLogger()
logger.setLevel("INFO")


def watch_queue():
    region_name = "us-east-1"

    session = boto3.session.Session()
    sqs = session.client(service_name='sqs', region_name=region_name)

    while True:
        response = sqs.receive_message(
            QueueUrl=os.getenv("QUEUE_URL", None),
            MessageSystemAttributeNames=['All'],
            MessageAttributeNames=['.*'],
            MaxNumberOfMessages=1,
            VisibilityTimeout=1200,
            # WaitTimeSeconds=10,
        )

        if response and 'Messages' in response:
            receipt = response['Messages'][0]['ReceiptHandle']
            event = json.loads(response['Messages'][0]['Body'])
            if 'Records' in event and 's3' in event['Records'][0]:
                try:
                    bucket = event['Records'][0]['s3']['bucket']['name']
                    file = event['Records'][0]['s3']['object']['key']
                    logger.info(f"Received Event from Bucket {bucket}, File {file}")
                    service_validate(bucket, file)

                    # delete message after successfully processing the file
                    response = sqs.delete_message(QueueUrl=os.getenv("QUEUE_URL", None), ReceiptHandle=receipt)

                except Exception as e:
                    logger.exception("Error processing S3 SQS message event.", e)
            else:
                # if a message comes in that isn't part of our S3 events, delete from queue
                response = sqs.delete_message(QueueUrl=os.getenv("QUEUE_URL", None), ReceiptHandle=receipt)


if __name__ == '__main__':
    watch_queue()
