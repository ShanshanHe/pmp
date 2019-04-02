FROM rabbitmq:3.7-management

COPY etabotsite/custom_settings.json /custom_settings.json
COPY rabbitmq/conf_rabbitmq.py /conf_rabbitmq.py

RUN python /conf_rabbitmq.py
