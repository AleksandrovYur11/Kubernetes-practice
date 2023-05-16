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