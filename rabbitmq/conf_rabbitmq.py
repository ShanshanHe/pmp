import sys
import json

with open('/custom_settings.json') as f:
# with open('../etabotsite/custom_settings.json') as f:
    settings = json.load(f)

rmq_user = settings['RMQ_USER']
rmq_pass = settings['RMQ_PASS']
rmq_host = settings['RMQ_HOST']
rmq_vhost = settings['RMQ_VHOST']

rabbitconf = """default_vhost = {vhost}
default_user = {user}
default_pass = {pword}""".format(
    vhost=rmq_vhost, user=rmq_user, pword=rmq_pass)

with open('/etc/rabbitmq/rabbitmq.conf-py', 'w+') as f:
# with open('rabbitmq.conf', 'w+') as f:
    f.write(rabbitconf)

with open('/etc/hostname', 'w+') as f:
    f.write(rmq_host)

with open('/etc/hosts', 'a') as f:
    f.write('127.0.0.1 ' + rmq_host)
