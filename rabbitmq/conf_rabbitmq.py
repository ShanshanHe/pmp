"""Writes configuration file for RabbitMQ messenger."""

import sys
import json
import logging

with open('/custom_settings.json') as f:
    settings = json.load(f)

rmq_user = settings.get('RMQ_USER')
rmq_pass = settings.get('RMQ_PASS')
rmq_vhost = settings.get('RMQ_VHOST')

if rmq_user is not None and rmq_pass is not None and rmq_vhost is not None:
    rabbitconf = """default_vhost = {vhost}
    default_user = {user}
    default_pass = {pword}
    """.format(
        vhost=rmq_vhost, user=rmq_user, pword=rmq_pass)

    with open('/etc/rabbitmq/rabbitmq.conf', 'w+') as f:
        f.write(rabbitconf)
else:
    logging.warning('not enough Rabbitmq settings. \
Need RMQ_USER, RMQ_PASS, RMQ_VHOST in custom_settings.json')
