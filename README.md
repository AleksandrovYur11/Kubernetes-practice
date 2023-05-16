##ITMO Kubernetes_homework
***
####__Задачи__:
1. В качестве web-сервера для простоты можно воспользоваться Python: “python -m http.server 8000”. 
    1. Добавьте эту команду в инструкцию CMD в Dockerfile.
2. Создать Dockerfile на основе “python:3.10-alpine”, в котором.
    1. Создать каталог “/app” и назначить его как WORKDIR.
    2. Добавить в него файл, содержащий текст “Hello world”.
    3. Обеспечить запуск web-сервера от имени пользователя с “uid 1001”.
3. Собрать Docker image с tag “1.0.0”.
4. Запустить Docker container и проверить, что web-приложение работает.
5. Выложить image на Docker Hub.
6. Создать Kubernetes Deployment manifest, запускающий container из созданного image.
    1. Имя Deployment должно быть “web”.
    2. Количество запущенных реплик должно равняться двум.
    3. Добавить использование Probes.
7. Установить manifest в кластер Kubernetes.
8. Обеспечить доступ к web-приложению внутри кластера и проверить его работу
    1. Воспользоваться командой kubectl port-forward: “kubectl port-forward --address 0.0.0.0 deployment/web 8080:8000”.
    2. Перейти по адресу http://127.0.0.1:8080/hello.html.
***
####__Решение:__
#####___Этап 1:___

Напишем сервер, для его создания используется фреймворк Flask:

```
from flask import Flask,render_template

app=Flask(__name__,template_folder='template')


@app.route('/hello.html')
def hello_world():
    return render_template('hello.html')
```
А также hello.html: 

```
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>
      red01!
    </title>
  </head>
  <body>
    Hello World!
  </body>
</html>
```
***
#####___Этап 2:___
Создание Dockerfile в котором описана сборка сервера:

```
# Based image
FROM python:3.10-alpine

# Variables required for enviroment creation
ARG USER=app
ARG UID=1001
ARG GID=1001

# Framework installation
RUN pip install --no-cache-dir Flask==2.2.*

# Creating OS user and home directory
RUN addgroup -g ${GID} -S ${USER} \
   && adduser -u ${UID} -S ${USER} -G ${USER} \
   && mkdir -p /app \
   && chown -R ${USER}:${USER} /app
USER ${USER}

# Entering home dir /app
WORKDIR /app


# Enviroment variables required for launching web-application
ENV FLASK_APP=server.py \
   FLASK_RUN_HOST="0.0.0.0" \
   FLASK_RUN_PORT="8000" \
   PYTHONUNBUFFERED=1

# Copying application code to home directory
COPY --chown=$USER:$USER . /app

# Publishing the port that the application is listening on
EXPOSE 8000

# Application launch command
CMD ["flask", "run"]
```

***

#####___Этап 3:___

Далее создаём Docker image с тегом 1.0.0:
```
docker build -t aleksandrovyur11/server:1.0.0 --network host -t aleksandrovyur11/server:latest ./server
```
Список image:
```
$ sudo docker images
REPOSITORY                TAG       IMAGE ID       CREATED         SIZE
aleksandrovyur11/server   1.0.0     ffd813ac8dd3   2 minutes ago   60.7MB
aleksandrovyur11/server   latest    ffd813ac8dd3   2 minutes ago   60.7MB
```
***

#####___Этап 4:___

Далее запустим создадим container и запустим приложение:

```
$ sudo docker run -ti --rm -p 8000:8000 --name server aleksandrovyur11/server:1.0.0
 * Serving Flask app 'server.py'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8000
 * Running on http://172.17.0.2:8000
Press CTRL+C to quit
172.17.0.1 - - [15/May/2023 15:28:47] "GET /hello.html HTTP/1.1" 200 -
```
Проверим работу приложения:

```
$ curl http://127.0.0.1:8000/hello.html
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>
      red01!
    </title>
  </head>
  <body>
    Hello World!
  </body>
</html>a
```
Приложение работает корректно.

***

#####___Этап 5:___
Сделаем Push images в DockerHub:
```
$ sudo docker push aleksandrovyur11/server:1.0.0
```
Откроем web-интерфейс Docker Hub по адресу https://hub.docker.com/ и найдем загруженный image

![Screenshot](/server/images/DockerHub.png)

***

#####___Этап 6:___
Создадим Kubernetes Deployment manifest, запускающий container из созданного image.
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kuber
  labels:
    app: server
spec:
  replicas: 2
  selector:
    matchLabels:
      app: server
  template:
    metadata:
      labels:
        app: server
    spec:
      containers:
      - name: server
        image: aleksandrovyur11/server:1.0.0
        ports:
        - containerPort: 8000
        livenessProbe:
            httpGet:
              path: /hello.html
              port: 8000
            initialDelaySeconds: 3
            periodSeconds: 3
```

***

#####___Этап 7:___
Установим manifest в кластер Kubernetes.


```
$ kubectl apply --filename deployment.yaml --namespace default
deployment.apps/kuber created
$ kubectl get pods --namespace default
NAME                                  READY   STATUS              RESTARTS        AGE
kuber-7fd5bf4479-k9d7w                0/1     ContainerCreating   0               17s
kuber-7fd5bf4479-r9rlv                0/1     ContainerCreating   0               17s
```
***
#####___Этап 8:___



Обеспечим доступ к web-приложению внутри кластера и проверим его работу.
```
$ kubectl port-forward --address 0.0.0.0 deployment/kuber 8080:8000
Forwarding from 0.0.0.0:8080 -> 8000
Handling connection for 8080
```
Проверка:
```
$ curl http://127.0.0.1:8000/hello.html
<!DOCTYPE html>
<html lang="en">
  <head>
    <title>
      red01!
    </title>
  </head>
  <body>
    Hello World!
  </body>
</html>a
```
Выведем информацию об развертывании:

```
$ kubectl describe deployment kuber
Name:                   kuber
Namespace:              default
CreationTimestamp:      Mon, 15 May 2023 19:48:51 +0300
Labels:                 app=server
Annotations:            deployment.kubernetes.io/revision: 1
Selector:               app=server
Replicas:               2 desired | 2 updated | 2 total | 2 available | 0 unavailable
StrategyType:           RollingUpdate
MinReadySeconds:        0
RollingUpdateStrategy:  25% max unavailable, 25% max surge
Pod Template:
  Labels:  app=server
  Containers:
   server:
    Image:        aleksandrovyur11/server:1.0.0
    Port:         8000/TCP
    Host Port:    0/TCP
    Liveness:     http-get http://:8000/hello.html delay=3s timeout=1s period=3s #success=1 #failure=3
    Environment:  <none>
    Mounts:       <none>
  Volumes:        <none>
Conditions:
  Type           Status  Reason
  ----           ------  ------
  Available      True    MinimumReplicasAvailable
  Progressing    True    NewReplicaSetAvailable
OldReplicaSets:  <none>
NewReplicaSet:   kuber-7fd5bf4479 (2/2 replicas created)
Events:          <none>
```



