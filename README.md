# pmp

backend data infrastructure and server for Smart project management tool made for teams to meet their deadline


## To deploy pmp, please follow the instructions below:

#### Prequisites:
* Have docker, docker compose installed
* Knowledge of Django and Nginx

#### Bring up pmp services which include nginx and django
Clone the repo to your server, and at the root directory, run the following command:
```
$ docker-compose build --no-cache
$ docker-compose up --no-start --force-recreate
```

It will build two docker images: `pmp-nginx` and `pmp-django`, and run both images as two containers. At the same time, it creates two docker local volumes:

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
