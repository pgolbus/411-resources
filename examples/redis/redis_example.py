from contextlib import contextmanager
import json

import redis
import requests

from utils import timer


@timer
def request(env):
    try:
        headers = {
            'X-RapidAPI-Key': env["api_key"],
            'X-RapidAPI-Host': env["api_host"]
        }
        with requests.get(env["api_url"], headers=headers) as r:
            word = r.json()[0]["word"]
            print(word)
            return word
    except Exception as e:
        print(r)

@contextmanager
def redis_connect(env):
    conn = redis.Redis(host=env["redis_host"], port=env["redis_port"], db=0)
    try:
        yield conn
    finally:
        conn.close()

@timer
def redis_write(conn, content):
    conn.set('content', content)

@timer
def redis_read(conn):
    value = conn.get('content')
    print(value.decode("UTF-8"))


if __name__ == "__main__":
    with open("env.json", "r") as fh:
        env = json.load(fh)
    content = request(env)
    with redis_connect(env) as conn:
        redis_write(conn, content)
        for _ in range(10):
            redis_read(conn)
