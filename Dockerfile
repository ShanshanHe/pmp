# Dockerfile

# FROM directive instructing base image to build upon
FROM python:3.6 

# File Author / Maintainer
MAINTAINER Maintaner Shanshan He

ADD . /my_application

RUN pip install -r my_application/requirements.txt

# EXPOSE port 8000 to allow communication to/from server
EXPOSE 8000

WORKDIR my_application/etabotsite/

# CMD specifcies the command to execute to start the server running.
CMD ["../start.sh"]
# done!
