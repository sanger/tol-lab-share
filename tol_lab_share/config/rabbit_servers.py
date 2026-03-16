import os
from lab_share_lib.config.rabbit_server_details import RabbitServerDetails

MLWH_RABBIT_SERVER = RabbitServerDetails(
    uses_ssl=False,
    host=os.environ.get("WAREHOUSE_RMQ_HOST", "127.0.0.1"),
    port=5672,
    username=os.environ.get("WAREHOUSE_RMQ_USER", "admin"),
    password=os.environ.get("WAREHOUSE_RMQ_PASSWORD", "development"),
    vhost="mlwh",
)

RABBIT_SERVER_DETAILS = RabbitServerDetails(
    uses_ssl=False,
    host=os.environ.get("LOCALHOST", "127.0.0.1"),
    port=5672,
    username=os.environ.get("RABBITMQ_USER", "admin"),
    password=os.environ.get("RABBITMQ_PASSWORD", "development"),
    vhost="tol",
)

TOL_RABBIT_SERVER = RABBIT_SERVER_DETAILS
ISG_RABBIT_SERVER = RABBIT_SERVER_DETAILS
