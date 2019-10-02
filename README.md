# pmp

backend data infrastructure and server for Smart project management tool made for teams to meet their deadline


## To deploy pmp, please follow the instructions below:

#### Prequisites:
* Have docker, docker compose installed
* Knowledge of Django and Nginx
* If needed add your dns to hosts for testing with your url locally, for example:
  ``` 
  $ sudo vi /etc/hosts
  ```
  Add the following line to the end of the file:
  ```
  127.0.0.1 <your web-app url, e.g. app.etabot.ai>
  ```

* Optionally to start, required for full operation:
- create/get the following json files in/etabotsite (see descriptions in "Settings jsons" section)
    1. custom_settings.json - general custom settings (end points, database, messenging service, etc)
    2. django_keys_prod.json - Django encryption keys used in production mode
    3. sys_email_settings.json - used for email communication setup
- git http url to an ETA algorithm

#### Bring up pmp services which include nginx and django
Clone the repo to your server
```
git clone https://github.com/ShanshanHe/pmp.git
```

### Configure pmp
- add custom_settings.json to etabotsite directory
- add django_keys_prod.json with your secret keys etabotsite directory (same format as django_keys.json)
- add sys_email_settings.json to etabotsite directory
- add ETA algorithm as a git submodule (see section "Optinal: connecting ETA algorithm instead of a placeholder")

### Build docker images and create volumes
At the root directory, run the following commands:
```
$ docker-compose build --no-cache
$ docker-compose up --no-start --force-recreate
```

The two commands above will build two docker images: `pmp-nginx` and `pmp-django`, and then run both images as two containers. At the same time, they create two docker local volumes, you can check the volumes using the following command:

```
$ docker volume ls
DRIVER              VOLUME NAME
local               pmp_pmp-django-static
local               pmp_pmp-nginx-cert
```

In our nginx, we have SSL enabled, so please make sure you have certificates ready. Now we are going to create a temporary container to load the certificate files onto the `pmp_pmp-nginx-cert` volume for nginx to use. Volume data persists outside of a containers lifetime and so even when we have finished with this temporary volume the certificate files will still be there for the nginx service to see.
```
$ docker run --name temp-volume -v pmp_pmp-nginx-cert:/etc/ssl/certs busybox
```
Here we are creating the container `temp-volume` using the busybox base image and using the same named volume `pmp_pmp-nginx-cert` mounted to the same path in the container as the nginx service would.
Note: Using the same mount path is not necessary.
The previous command will create the container but it will exit immediately but we dont need it running to manage the volume.
We now copy our certificate files to the volume through this container. The following commands copy these certs and rename these files to the `pmp_pmp-nginx-cert` volume via the `temp_volume` container.
```
$ docker cp nginx/certs/cert.pem temp-volume:/etc/ssl/certs/cert.pem
$ docker cp nginx/certs/key.pem temp-volume:/etc/ssl/certs/key.pem
```

### Running docker containers
Now we run the following commands again:
```
$ docker-compose build --no-cache
$ docker-compose up --force-recreate
```
Ensure all containers are up and running by:
```
$ docker ps
```
And you should see three containers running.

if you do not want celery container that runs periodic tasks - stop it by:
```
docker stop <container_id>
```
where <container_id> can be found from the earlier docker ps command

if you want to start the celery container on another machine, run this after images are built instead of docker-compose up
```
docker run pmp_celery
```

Vola, you successfully deployed your `pmp` project! Type the ip address of your server in your browser to visit the default `pmp` webpage. 

Hope you enjoy!

## To run django seperately for development, please follow the process below:

#### Prerequisite:
* Have python 3.6 installed on your development machine
* Add your dns to hosts, for example:
  ``` 
  $ sudo vi /etc/hosts
  ```
  Add the following line to the end of the file:
  ```
  127.0.0.1 app.etabot.ai
  ```

If you already know how to create a python virtual environment, you can skip this section, and directly go to *Run django server locally* section.

#### Install virtual environment management tool
E.g. virtualenv or conda

### virtualenv option

Install `virtualenv` and `virtualenvwrapper` tool to manage python environment
```
$ pip install virtualenv
$ pip install virtualenvwrapper
```
Open your bash profile:
```
$ vim ~/.bash_profile
```
and add the following two lines at the end of the file:
```
export WORKON_HOME=~/Envs
source /usr/local/bin/virtualenvwrapper.sh
```
And at your terminal, run:
```
$ source ~/.bash_profile
```

To create a virtual environment for the project, follow the command below:
```
$ mkvirtualenv --python=python3 <name_of_the_virtual_environment>
```

### conda option
follow https://docs.conda.io/projects/conda/en/latest/user-guide/install/

#### Run django server locally
Suppose you're already in a virtual environemnt, go to our project root directory,install the dependencies:
```
$ pip install -r requirements.txt
```
Go the etabotsite directory:
```
$ cd etabotsite/
```

Follow instructions in section "Configure pmp" above

If this is your first time running the project in development mode, you want to create the database table by running the following command:
```
$ python manage.py migrate
$ python manage.py makemigrations
```
To run all the unit tests:
```
$ python manage.py test
```

To run the backend server:
```
$ python manage.py runserver 127.0.0.1:8000
```

Vola! You have django server up and running in development mode. Go to you browser, enter the address below:
http://<url you set in etc/hosts>:8000/index
You have a sample project management site ready to go!

#### Advanced settings

### Settings jsons

## custom_settings.json - general custom settings
```
{
    "local_host_url":"<your local host url for testing, e.g. http://127.0.0.1:8000">,
    "prod_host_url":"<your production host url for testing, e.g. https://app.etabot.ai>"

    "db":"Django database definition. If no such key found, a local sqlite3 database will be used."

    "MESSAGE_BROKER":"rabbitmq" or "aws",
    # in case of rabbitmq:
    "RMQ_USER" : "username",
    "RMQ_PASS" : "password",
    "RMQ_HOST" : "host, e.g. host.docker.internal or 127.0.0.1 or other",
    "RMQ_VHOST" : "e.g. etabotvhost",
    # in case of aws:
    "AWS_ACCESS_KEY_ID":"Amazon services access key id for SQS messenging"
    "AWS_SECRET_ACCESS_KEY":"Amazon services access key for SQS messenging"

    "eta_crontab_args":<dictionary with crontab settings for example: 'eta_crontab_args':{'hour': 8}
                        see celery.schedules.crontab documentation for details>
}
```

Note: for accessing services on the same host as the docker container, use "host.docker.internal" for MacOS and Windows.
For Linux, until this is fixed (https://github.com/docker/libnetwork/pull/2348), use --network="host" in your docker run command, then 127.0.0.1 in your docker container will point to your docker host.


## django_keys.json - Django encryption keys used in development mode
```
{
    "DJANGO_SECRET_KEY":"Django secret key"
    "DJANGO_FIELD_ENCRYPT_KEY":"Django secret key used for encryption in databased fields"
}
```
run this from /etabotsite to generate a key:
```
$ python generate_key.py
```

## django_keys_prod.json
same as django_keys.json but keys for production. Keys will be checked against exposed dev keys from git repo.

## sys_email_settings.json - used for email communication setup
```
    "DJANGO_SYS_EMAIL": "username for email server",
    "DJANGO_SYS_EMAIL_PWD":"password for email server",
    "DJANGO_EMAIL_HOST":"email server host, e.g. smtp.sendgrid.net",
    "DJANGO_EMAIL_USE_TLS":bool for TLS,
    "DJANGO_EMAIL_PORT":email server port number port number,
    "DJANGO_EMAIL_TOKEN_EXPIRATION_PERIOD_S":Django email token expiration period in seconds (86400 = 24h)
```


### server end-point selection
By default, if you run server on MacOS (Darwin), it will detect you are in development mode and set host url to local_host_url (set in custom_settings.json or default value in settings.py) and set it correspondingly in UI API endpoint and email links. If OS other than Darwin, prod_host_url (set to value in custom_settings.json or default value in settings.py) will be used.


To modify the `/static/ng2_app/main.js` static file to point to API endpoint other than host urls as described above you can follow the commands below:
```
$ cd etabotapp/
$ python set_api_url.py static/ng2_app/ <end point url, e.g. http://app.etabot.ai:8000/api/>
```



#### Optinal: connecting ETA algorithm instead of a placeholder
```
$ cd etabotsite/
$ git submodule add <your git URL to repo called "etabot_algo">
$ git reset HEAD -- .gitmodules
$ git reset HEAD -- etabot_algo
```

The repo must have module ETApredict.py following pattern ETApredict_placeholder.py

#### Periodic tasks with Celery

Celery container will start automatically with Docker deployment.

For manual start: in a separate terminal start process with:
```
$ celery -A etabotsite worker -l info
```

in another seprate terminal start a process with:
```
celery -A etabotsite beat -l INFO
```


#### Installation issues

### Issue "ImportError: The curl client requires the pycurl library." 
can be resolved on Mac with:
```
pip uninstall pycurl
pip install --install-option="--with-openssl" --install-option="--openssl-dir=/usr/local/opt/openssl" pycurl
```

### Cannot uninstall XXX. It is a distutils installed project ...
E.g.: Cannot uninstall 'certifi'. It is a distutils installed project and thus we cannot accurately determine which files belong to it which would lead to only a partial uninstall.

solution

```
pip install -r requirements.txt --ignore-installed
```
Or per package:

```
pip install --ignore-installed ${PACKAGE_NAME}
```

E.g.
```
pip install --ignore-installed certifi
```

### celery issue with pycurl
start python and make sure you can import pycurl
if not, try 
```
conda install pycurl
```

### Networking errors
add the following lines in case you run into Networking errors:
Edit /etc/default/docker and add your DNS server to the following line:

Example 
DOCKER_OPTS="--dns 8.8.8.8 --dns 10.252.252.252"


#### Maintenance

To free up space from unused stale containers:
```
docker images -q --filter dangling=true | xargs docker rmi
```