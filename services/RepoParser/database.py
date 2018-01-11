import config
import json
import psycopg2
import psycopg2.extras
from datetime import datetime

def get(path):
    """
    Lookup repo in repo table based on path column.
    """

    statement = """
                SELECT *
                FROM repo
                WHERE path = %s;
                """
    args = [path]

    with psycopg2.connect(
        dbname=config.db['name'],
        host=config.db['host'],
        port=config.db['port'],
        user=config.db['username'],
        password=config.db['password']
        ) as connection:
        with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(statement, args)
            if cursor.rowcount > 0:
                column_names = [desc[0] for desc in cursor.description]
                data = cursor.fetchone()
                result = dict(zip(column_names, data))
            else:
                result = None
    connection.close()

    return result

def add(path, results):
    """
    Add new repo to repo table.
    """

    statement = """
                INSERT INTO repo (path, details, status, created_at, modified_at)
                VALUES (%s, %s, %s, %s, %s);
                """
    args = [path, json.dumps(results), 'active', datetime.utcnow(), datetime.utcnow()]

    return transact(statement, args)

def update(path, results):
    """
    Update existing repo data.
    """
    statement = """
                UPDATE repo
                SET details = %s, modified_at = %s
                WHERE path = %s
                """
    args = [json.dumps(results), datetime.utcnow(), path]

    return transact(statement, args)

def transact(statement, args):
    """
    Helper function for writing to repo table.
    """
    with psycopg2.connect(
        dbname=config.db['name'],
        host=config.db['host'],
        port=config.db['port'],
        user=config.db['username'],
        password=config.db['password']
        ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(statement, args)

    connection.close()
