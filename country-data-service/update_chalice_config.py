import json
import os

def update_chalice_config():
    config_path = '.chalice/config.json'
    with open(config_path, 'r') as f:
        config = json.load(f)

    config['stages']['dev']['iam_role_arn'] = os.environ['IAM_ROLE_ARN']
    config['stages']['dev']['environment_variables']['SQS_QUEUE_URL'] = os.environ['SQS_QUEUE_URL']
    config['stages']['dev']['environment_variables']['REDIS_HOST'] = os.environ['REDIS_HOST']
    config['stages']['dev']['environment_variables']['REDIS_PORT'] = os.environ['REDIS_PORT']
    config['stages']['dev']['subnet_ids'] = os.environ['SUBNET_IDS'].split(',')
    config['stages']['dev']['security_group_ids'] = [os.environ['SECURITY_GROUP_ID']]

    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)

if __name__ == '__main__':
    update_chalice_config()