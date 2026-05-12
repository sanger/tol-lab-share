How to run
----------

0. Spin up the required dependency containers:

```bash
../docker/dependencies/up.sh
python setup_dev_rabbit.py
```

1. Create a docker image for the project that we will use to run the code.
This saves a lot of problems when installing dependent libraries in local.
To build you have to reference to the root folder of the project that contains the
Dockerfile file, for example, if you run the command from inside this folder it should be:

```bash
  docker build ../../ -t tol-lab-share:develop
```

2. Create a file .env with this content (fill in the data on the entries that have ...):

```
SETTINGS_MODULE=tol_lab_share.config.defaults
LOCALHOST=host.docker.internal
REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
REDPANDA_URL=...
RABBITMQ_HOST=...
RABBITMQ_USERNAME=...
RABBITMQ_PASSWORD=...
TRACTION_API_KEY=...
TRACTION_API_KEY_HEADER=...
```

An example .env file for local development:

```
SETTINGS_MODULE=tol_lab_share.config.defaults
LOCALHOST=host.docker.internal
REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
REDPANDA_URL=http://host.docker.internal:8081
RABBITMQ_HOST=host.docker.internal
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=admin
RABBITMQ_PASSWORD=development
TRACTION_API_KEY=traction-development
TRACTION_API_KEY_HEADER=X-Traction-Client-Id
```

3. Run the previously created image using the env variables defined in
the previous step:

```bash
   docker run -ti -v $(pwd):/code -v /etc/ssl/certs/ca-certificates.crt:/etc/ssl/certs/ca-certificates.crt:ro --env-file=.env --entrypoint bash tol-lab-share:develop
```

4. Inside this new bash we can run the command using pipenv:

Note: Set the flag uses_ssl=False in tools/demo/publisher.py for local development to disable the use of ssl.

```bash
   pipenv run python tools/demo/publisher.py --unique_id={your_unique_id} --message_types={message_choice}
```

The Unique ID lets you identify the generated messages more easily and will form part of the messages sent.
The message types defines which types of message will be sent.
To see valid values for `message_types` leave the value out of your run command and the usage will tell you the valid values you can choose from.
