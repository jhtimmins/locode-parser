import boto3
import config
import json
from datetime import datetime, timezone
from services.RepoParser import parser, database

def get_message():
    """
    Retrieve repo by dequeuing message from SQS.
    """
    aws_client = boto3.client('sqs', region_name=config.sqs['region'])

    response = aws_client.receive_message(
        QueueUrl=config.sqs['repo_url'],
        MessageAttributeNames=['repo'],
        MaxNumberOfMessages=1,
    )

    if 'Messages' not in response:
        return []

    return response['Messages'][0]


def parse_repo(message):
    """
    Grab Github contents for named repo, parse repo, upload results to DB.
    """
    body = json.loads(message['Body'])
    existing_results = database.get(body['repo'])
    if existing_results:
        elapsed_time = datetime.now(timezone.utc) - existing_results['modified_at']
        if elapsed_time.total_seconds() > 24 * 3600:
            results = parser.load(body['repo'])
            if results:
                database.update(body['repo'], results)

    else:
        results = parser.load(body['repo'])
        if results:
            database.add(body['repo'], results)


def lambda_handler(event, context):
    """
    Initialize Lambda function by grabbing message from queue
    and parsing repo data from Github.
    """
    message = get_message()
    parse_repo(message)

lambda_handler("", "")
