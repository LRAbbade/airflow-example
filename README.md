# Install docker

Atualize sua lista de pacotes:

```sh
sudo apt update
```

Instale alguns pacotes que permitem que o apt utilize pacotes via HTTPS:

```sh
sudo apt install apt-transport-https ca-certificates curl software-properties-common
```

Então, adicione a chave GPG para o repositório oficial do Docker em seu sistema:

```sh
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
```

Adicione o repositório do Docker às fontes do APT:

```sh
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu bionic stable"
```

A seguir, atualize o banco de pacotes com os pacotes Docker do repositório recém adicionado:

```sh
sudo apt update
```

Finalmente, instale o Docker:

```sh
sudo apt install docker-ce
```

O Docker agora deve ser instalado, o daemon iniciado e o processo ativado para iniciar na inicialização. Verifique se ele está sendo executado:

```sh
$ sudo systemctl status docker
● docker.service - Docker Application Container Engine
   Loaded: loaded (/lib/systemd/system/docker.service; enabled; vendor preset: enabled)
   Active: active (running) since Thu 2018-07-05 15:08:39 UTC; 2min 55s ago
     Docs: https://docs.docker.com
 Main PID: 10096 (dockerd)
    Tasks: 16
   CGroup: /system.slice/docker.service
           ├─10096 /usr/bin/dockerd -H fd://
           └─10113 docker-containerd --config /var/run/docker/containerd/containerd.toml
```

## Executando o Comando Docker sem Sudo

```sh
sudo usermod -aG docker ${USER}
```

Faca login novamente:

```sh
su - ${USER}
```

Confirme que o usuario pertence ao grupo docker:

```sh
id -nG
```

## Docker compose

```sh
sudo apt  install docker-compose
docker-compose -f docker-compose.yaml up -d
```

Don't forget to set entrypoint on docker-compose file

## Airflow setup in docker

First we are using the [non-oficial image](https://hub.docker.com/r/puckel/docker-airflow) (no oficial available)

We have some proprietary packages from gitlab on our projects, than we need to get an valid ssh key to install the packages in our docker.
Although, keep the key with access to gitlab isn't a good practice and pass the key as an env variable exposes it on docker history.
To solve this problem, we apply the multi-stage build concept (https://vsupalov.com/build-docker-image-clone-private-repo-ssh-key/).

This creates an intermediate container to install some dependences and than import the real image, destroying the intermediate but keeping useful folders.
In this context, we use a Dockerfile to build the intermediate, install dependences and copy de env to the airflow image

```dockerfile
# this is our first build stage, it will not persist in the final image
# we will use this to install requirements that require ssh access touch
# private repos
FROM python:3.7 AS intermediate
# create and change working directory
WORKDIR /root
# Add credentials on build
ARG SSH_PRIVATE_KEY
RUN mkdir -p /root/.ssh
# remember to use a temporary variable for this
# This private key shouldn't be saved in env files
RUN echo "${SSH_PRIVATE_KEY}" >> /root/.ssh/id_rsa && chmod 600 /root/.ssh/id_rsa
# make sure your domain is accepted
RUN touch /root/.ssh/known_hosts
RUN ssh-keyscan -t rsa gitlab.gscap.com.br >> /root/.ssh/known_hosts
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install git+ssh://git@gitlab.gscap.com.br/khan/arlyn_py.git@master#egg=arlyn_py 
#khan-py==1.0.871
#vith-py==1.1.0
# WORKDIR ~/arlyn_py
# RUN python setup.py install --user
# image that would be used
FROM puckel/docker-airflow:1.10.6
# copy the python packages from the intermediate image
# RUN pip list
# RUN pip show arlyn-py
COPY --from=intermediate /usr/local/lib/python3.7/site-packages/ /usr/local/lib/python3.7/site-packages/
ENV PYTHONUNBUFFERED 1
```
