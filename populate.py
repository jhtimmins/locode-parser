import boto3
import config
import json
import requests

def get_repos():
    """
    Lookup most popular repos on Github based on stars.
    """
    username = config.github['username']
    password = config.github['password']
    repos = []
    page = 1
    while len(repos) < 1000:
        url = "https://api.github.com/search/repositories?q=stars:>=1&sort=stars&order=desc&page={}".format(page)
        contents_string = requests.get(url, auth=(username, password))
        contents = contents_string.json()
        if 'items' in contents:
            for item in contents['items']:
                 repos.append(item['full_name'])

    return repos

def queue_repos(repos):
    """
    Queue repos by name in SQS.
    """
    aws_client = boto3.client('sqs', region_name=config.sqs['region'])

    for repo in repos:
        response = aws_client.send_message(
            QueueUrl=config.sqs['repo_url'],
            MessageBody=json.dumps({'repo': repo}),
        )

    return response


if __name__ == "__main__":
    repos = get_repos()
    queue_repos(repos)
