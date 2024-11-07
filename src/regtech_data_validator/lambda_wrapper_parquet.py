from regtech_data_validator.service_parquet import service_validate_parquet


def lambda_handler(event, context):
    request = event['responsePayload'] if 'responsePayload' in event else event

    bucket = request['Records'][0]['s3']['bucket']['name']
    file = request['Records'][0]['s3']['object']['key']
    service_validate_parquet(bucket, file)


# def test():
#     event = {
#         "Records": [{
#             "s3": {
#                 "bucket": {
#                     "name": "cfpb-regtech-devpub-lc-test"
#                 },
#                 "object": {
#                     "key": "upload/2024/1234364890REGTECH006/6265_pqs/"
#                 },
#             }}
#         ]
#     }
#     # s3://cfpb-regtech-devpub-lc-test/upload/2024/1234364890REGTECH006/6254.csv/
#     lambda_handler(event, None)


# if __name__ == "__main__":
#     test()