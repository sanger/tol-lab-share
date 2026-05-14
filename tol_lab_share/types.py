from types import ModuleType
from typing import Any, Literal


class Config(ModuleType):
    """ModuleType class for the app config."""

    LOGGING: dict[str, Any]

    # RabbitMQ
    RABBITMQ_HOST: str
    RABBITMQ_SSL: bool
    RABBITMQ_PORT: int
    RABBITMQ_USERNAME: str
    RABBITMQ_PASSWORD: str
    RABBITMQ_VHOST: str
    RABBITMQ_CRUD_QUEUE: str
    RABBITMQ_FEEDBACK_EXCHANGE: str
    RABBITMQ_PUBLISH_RETRY_DELAY: int
    RABBITMQ_PUBLISH_RETRIES: int
    SELECTED_ENCODER_FOR_FEEDBACK_MESSAGE: Literal["json", "binary"]

    # RedPanda
    REDPANDA_BASE_URI: str

    # Traction
    TRACTION_URL: str
    TRACTION_QC_URL: str
    TRACTION_API_KEY: str
    TRACTION_API_KEY_HEADER: str

    PROCESSORS: dict[str, str]

    CERTIFICATES_VALIDATION_ENABLED: bool
    EBI_TAXONOMY_URL: str
    LOCALHOST: str
    ROOT_PASSWORD: str
