import os
import json
import datetime


def lambda_handler(event, context):
    today = datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=9))).date()
    print(f'subfunction called {today}')
    print(f'payload from main function: {event}')

    return {
        'statusCode': 200,
        'body': json.dumps('Finished sub function')
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
