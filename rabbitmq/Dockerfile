FROM rabbitmq:3.7-management

ADD rabbitmq/rabbitmq.config /etc/rabbitmq/
ADD rabbitmq/definitions.json /etc/rabbitmq/
RUN chown rabbitmq:rabbitmq /etc/rabbitmq/rabbitmq.config /etc/rabbitmq/definitions.json
CMD ["rabbitmq-server"]
