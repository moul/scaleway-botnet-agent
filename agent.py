import json
import os
import re
import redis
import shlex
import sys
import urllib
import urllib2
from subprocess import Popen, PIPE, STDOUT, check_output

from celery import Celery


celery = Celery('tasks') #, broker=amqp, backend=amqp)


def get_metadata():
    try:
        return json.loads(urllib2.urlopen(
            'http://169.254.42.42/conf?format=json',
            None,
            3,
        ).read())
    except:
        return {'tags': []}


def get_external_ip():
    site = urllib.urlopen("http://checkip.dyndns.org/").read()
    grab = re.findall('([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)', site)
    address = grab[0]
    return address


# run_command Task
@celery.task(shared=True, time_limit=60)
def run_command(command):
    task_id = run_command.request.id
    lines = []
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
            lines.append(line)
            redis_instance.publish('task:{}:stdout'.format(task_id),
                                   line.rstrip())
        else:
            proc.wait()
            redis_instance.publish('task:{}:finish'.format(task_id),
                                   str(proc.returncode))
            break
    ret = {
        'retcode': proc.returncode,
        'output': lines,
    }
    print(ret)
    return ret


def main():
    # Configuration
    amqp_user = 'guest:guest'
    backend_host = '127.0.0.1'

    metadata = get_metadata()
    metadata_queues = []
    for tag in [tag.split('=') for tag in metadata.get('tags', [])]:
        if tag[0] == 'manager':
            backend_host = tag[1]
        if tag[0] == 'amqp-user':
            amqp_user = tag[1]
        if tag[0] == 'queues':
            metadata_queues = tag[1].split('|')

    amqp_user = os.environ.get('AMQP_USER', amqp_user)
    backend_host = os.environ.get('MASTER', backend_host)

    # Backends
    amqp = 'amqp://{}@{}:5672'.format(amqp_user, backend_host)

    queues = ['celery', get_external_ip()] + metadata_queues

    celery.conf['BROKER_URL'] = amqp
                    
    celery.select_queues(queues)

    redis_instance = redis.Redis(host=backend_host)


main()
