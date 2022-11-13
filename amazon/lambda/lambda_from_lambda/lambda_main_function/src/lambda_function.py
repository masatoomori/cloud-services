import os
import json
import logging

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

SUBFUNCTION_NAME = 'lambda_subfunction'


def lambda_handler(event, context):
    logger.info(json.dumps(event))

    client = boto3.client('lambda')
    client.invoke(
        FunctionName=SUBFUNCTION_NAME,
        InvocationType='Event',
        LogType='Tail',
        Payload=json.dumps(event)
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Finished main function')
    }


def test():
    deploy_path = os.path.join(os.pardir, 'deploy')
    invocation_file = os.path.join(deploy_path, 'input_for_invocation.json')
    if os.path.exists(invocation_file):
        event = json.load(open(invocation_file, 'r'))
        context = {}
        lambda_handler(event, context)
    else:
        print('No invocation file found')


if __name__ == '__main__':
    test()