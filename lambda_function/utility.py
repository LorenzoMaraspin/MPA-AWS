import boto3
from botocore.exceptions import ClientError
import json
import os
import re

def get_config(event):
    config = {
        'lambda': {
            'function_name': os.environ['AWS_LAMBDA_FUNCTION_NAME'],
            'region': os.environ['AWS_REGION'],
            'env': os.environ['ENV']
        },
        'secret': {
            'api_key': get_secret(os.environ['ENV'])['api_key'],
            'api_secret': get_secret(os.environ['ENV'])['api_secret']
        },
        'bybit': {
            "account_type": os.environ['BYBIT_ACCOUNT_TYPE'],
            "order_type": os.environ['BYBIT_ORDER_TYPE'],
            "category": os.environ['BYBIT_CATEGORY'],
            "market_unit": os.environ['BYBIT_MARKET_UNIT'],
            "is_leverage": os.environ['BYBIT_IS_LEVERAGE'],
            "trade_mode": int(os.environ['BYBIT_TRADE_MODE']),
            "buy_leverage": os.environ['BYBIT_BUY_LEVERAGE'],
            "sell_leverage": os.environ['BYBIT_SELL_LEVERAGE'],
            "trade_size": os.environ['BYBIT_SIZE_TRADE'],
            "symbol": os.environ['BYBIT_SYMBOL'],
            "trading_management": get_parameter_value(os.environ['BYBIT_TRADE_MANAGEMENT']),
            "trading_management_index": 0 if os.environ['BYBIT_TRADE_MANAGEMENT'] == 2 else int(os.environ['BYBIT_TRADE_INDEX'])
        },
        'event': {
            'message': event['message'],
            'side': "Buy" if 'Long' in event['message'] else "Sell",
            'price': re.findall(r'\d+\.?\d*', event['message'])[0]
        },
        'ssm': {
            'ops_1_name': os.environ['SSM_OPERATIVE_1_TRADE'],
            'ops_1_value': get_parameter_value(os.environ['SSM_OPERATIVE_1_TRADE']),
            'ops_2_name': os.environ['SSM_OPERATIVE_2_TRADE'],
            'ops_2_value': get_parameter_value(os.environ['SSM_OPERATIVE_2_TRADE']),
        }
    }
    return config

def can_deserialize(s):
    try:
        json.loads(s)
        return True
    except json.JSONDecodeError:
        return False

def get_parameter_value(parameter_name):
    ssm = boto3.client('ssm')
    try:
        response = ssm.get_parameter(Name=parameter_name)
        if can_deserialize(response['Parameter']['Value']):
            return json.loads(response['Parameter']['Value'])
        else:
            return response['Parameter']['Value']
    except ClientError as e:
        raise e

def get_secret(env):
    if env == 'dev':
        secret_name = os.environ['DEV_AWS_SECRET']
    else:
        secret_name = os.environ['PROD_AWS_SECRET']
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager')

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e

    secret = get_secret_value_response['SecretString']
    return json.loads(secret)