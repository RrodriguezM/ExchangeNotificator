import json
import boto3
import requests
import os


def lambda_handler(event, context):
    table_name = os.environ['TABLE_NAME']
    table = boto3.resource("dynamodb").Table(table_name)
    # table.put_item(Item={'Exchange': 'COP', 'Value': '42'})
    url = "http://api.exchangeratesapi.io/v1/latest?access_key=da9abc8c713d60756cf946aeaa8db55d"

    response = requests.request("GET", url)

    COP = response.json()["rates"]["COP"]
    USD = response.json()["rates"]["USD"]
    USD_to_COP = COP/USD
    intUSDtoCOP = int(USD_to_COP/100)


    # Read the dynamoDB
    response = table.get_item(
        Key={
            'Exchange': 'COP'
        }
    )
    current_exchange_window = response['Item']['Value']
    print(current_exchange_window)

    # current_exchange_window = Read from dynamo

    if intUSDtoCOP != int(current_exchange_window):
        # read the arn from a enviroment variable
        topic_arn = os.environ['SNS_TOPIC_ARN']

        # Send notification to SNS
        sns = boto3.client('sns')

        if intUSDtoCOP > int(current_exchange_window):
            Message = f'The exchange rate has increased!, New exchange rate is: {USD_to_COP}'
        else:
            Message = f'The exchange rate has decreased!, New exchange rate is: {USD_to_COP}'

        sns.publish(
            TopicArn=topic_arn,
            Message=Message,
            Subject='Exchange Rate Changed'
        )

        # Write to dynamoDB
        print("notification")
        table.put_item(Item={'Exchange': 'COP', 'Value': str(intUSDtoCOP)})

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "hello world",
        }),
    }
