import config
import requests

def validate(path):
    path = clean_path(path)
    repo = get_repo(path)
    if 'message' in repo and repo['message'] == 'Not Found':
        return False
    else:
        return path

def clean_path(path):
    # Remove arguments that might be used for redirect
    if '?' in path:
        path = path.split('?')[0]

    if 'github.com' in path:
        path = path.split('github.com')[1]

    if 'repos/' in path:
        path = path.split('repos/')[1]

    if path[0] == '/':
        path = path[1:]

    return path

def get_repo(path):
    url = "https://api.github.com/repos/" + path
    contents = requests.get(url, auth=(config.github['username'], config.github['password']))
    return contents.json()
