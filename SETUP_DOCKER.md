## Setting up a complete development environment from scratch

> If you already have a rabbitmq instance running via brew or similar, ensure you only have one instance 
> running at a time. You may run into networking issues if you rely on partial docker setup and partial local setup.
---

1. Start dependent services: RabbitMQ and RedPanda

    ```bash
    ./docker/dependencies/up.sh
    ```

1. Setup RabbitMQ configuration (queues, etc). You may need to wait 30 seconds from the previous command
to run this one as it requires Rabbitmq to have started completely:

    ```bash
    python setup_dev_rabbit.py
    ```

1. Load Redpanda schemas:

    ```bash
    ./schemas/push.sh http://localhost:8081
    ```

1. Build docker image

    ```bash
    docker build . -t tol-lab-share:develop
    ```

1. Create .env file with contents

    ```text
    SETTINGS_MODULE=tol_lab_share.config.defaults
    LOCALHOST=host.docker.internal
    REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
    REDPANDA_URL=http://host.docker.internal:8081
    RABBITMQ_HOST=host.docker.internal
    RABBITMQ_PORT=5672
    RABBITMQ_USERNAME=admin
    RABBITMQ_PASSWORD=development
    ```

1. Start interactive bash in docker container

    ```bash
    docker run -ti -v $(pwd):/code -v --env-file=.env --entrypoint bash tol-lab-share:develop
    ```

1. Start the consumer service (inside the previous bash)

    ```bash
    pipenv run python main.py
    ```

After this you should have:

* Consumer (python main.py) running connected to Rabbitmq queue
* Rabbitmq service running in http://localhost:8080/ with user/password: admin/development
* Redpanda API service running in local in http://localhost:8081/

If you want to perform any changes in code, you can kill the consumer with Control-C, modify the code in local and then restart the consumer again using the same command
