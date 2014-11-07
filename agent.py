import json
import os
import redis
import shlex
import sys
import urllib
from subprocess import Popen, PIPE, STDOUT, check_output

from celery import Celery


metadata = json.loads(urllib.urlopen(
    'http://169.254.42.42/conf?format=json'
).read())

# Configuration
amqp_user = 'guest:guest'
backend_host = '127.0.0.1'
for tag in [tag.split('=') for tag in metadata.get('tags', [])]:
    if tag[0] == 'manager':
        backend_host = tag[1]
    if tag[0] == 'amqp-user':
        amqp_user = tag[1]
amqp_user = os.environ.get('AMQP_USER', amqp_user)
backend_host = os.environ.get('MASTER', backend_host)

# Backends
amqp = 'amqp://{}@{}:5672'.format(amqp_user, backend_host)
celery = Celery('tasks', broker=amqp, backend=amqp)
redis_instance = redis.Redis(host=backend_host)

# run_command Task
@celery.task(shared=True, time_limit=60)
def run_command(command):
    task_id = run_command.request.id
    proc = Popen(
        ['/bin/bash', '-c', command],
        stdout=PIPE, stderr=STDOUT,
        env={'PATH': os.environ['PATH']},
    )

    redis_instance.publish('task:{}:pid'.format(task_id), 42)

    while True:
        line = proc.stdout.readline()
        if line:
            print(line)
            redis_instance.publish('task:{}:stdout'.format(task_id),
                                   line.rstrip())
        else:
            proc.wait()
            redis_instance.publish('task:{}:finish'.format(task_id),
                                   str(proc.returncode))
            break
    ret = {
        'retcode': proc.returncode,
    }
    print(ret)
    return ret
