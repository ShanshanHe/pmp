# pmp

backend data infrastructure and server for Smart project management tool made for teams to meet their deadline


## To deploy pmp, please follow the instructions below:

#### Prequisites:
* Have docker, docker compose installed
* Knowledge of Django and Nginx
* Add your dns to hosts for testing with your url locally, for example:
  ``` 
  $ sudo vi /etc/hosts
  ```
  Add the following line to the end of the file:
  ```
  127.0.0.1 <your web-app url, e.g. app.etabot.ai>
  ```

* Optionally: create "custom_settings.json" file in /etabotsite with the following

```
{
    "local_host_url":"<your local host url for testing, e.g. http://127.0.0.1:8000">,
    "prod_host_url":"<your production host url for testing, e.g. https://app.etabot.ai>"
}
```

#### Bring up pmp services which include nginx and django
Clone the repo to your server
```
git clone https://github.com/ShanshanHe/pmp.git
```

Add sys_email_settings.json like this to etabotsite directory:
```
{
    "DJANGO_SYS_EMAIL": "email",
    "DJANGO_SYS_EMAIL_PWD": "your_password",
    "DJANGO_EMAIL_HOST":"smtp.your.server", # e.g smtp.gmail.com
    "DJANGO_EMAIL_USE_TLS":true,
    "DJANGO_EMAIL_PORT":000,
    "DJANGO_EMAIL_TOKEN_EXPIRATION_PERIOD_S":86400
}
```

Add django_keys_prod.json with your secret keys etabotsite directory (same format as django_keys.json)

At the root directory, run the following commands:
```
$ docker-compose build --no-cache
$ docker-compose up --no-start --force-recreate
```
add the following lines in case you run into Networking errors:
Edit /etc/default/docker and add your DNS server to the following line:

Example 
DOCKER_OPTS="--dns 8.8.8.8 --dns 10.252.252.252"

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

Now we run the following commands again:
```
$ docker-compose build --no-cache
$ docker-compose up --force-recreate
```
Ensure all containers are up and running by:
```
$ docker ps
```
And you should see two containers running.

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
#### Install `virtualenv` and `virtualenvwrapper` tool to manage python environment
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
#### Run django server locally
Suppose you're already in a virtual environemnt, go to our project root directory,install the dependencies:
```
$ pip install -r requirements.txt
```
Go the etabotsite directory:
```
$ cd etabotsite/
```
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
http://app.etabot.ai:8000/index
You have a sample project management site ready to go!

#### Advanced settings

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
in a separate terminal start process with:
```
$ celery -A etabotsite worker -l info
```

in another seprate terminal start a process with:
```
celery -A etabotsite beat -l INFO
```
