# flake8: noqa
import os

from tol_lab_share.config.logging import *
from .rabbit import *

# If we're running in a container, then instead of localhost
# we want host.docker.internal, you can specify this in the
# .env file you use for docker. eg
# LOCALHOST=host.docker.internal
LOCALHOST = os.environ.get("LOCALHOST", "127.0.0.1")
ROOT_PASSWORD = os.environ.get("ROOT_PASSWORD", "")

###
# RedPanda details
###
REDPANDA_BASE_URI = f"http://{os.environ.get('LOCALHOST', '127.0.0.1')}:8081"

###
# Traction details
###
TRACTION_URL = f"http://{os.environ.get('TRACTION_URL', '127.0.0.1:3100')}/v1/receptions"
TRACTION_QC_URL = f"http://{os.environ.get('TRACTION_URL', '127.0.0.1:3100')}/v1/qc_receptions"
TRACTION_API_KEY = os.environ.get("TRACTION_API_KEY", "traction-development")
TRACTION_API_KEY_HEADER = os.environ.get("TRACTION_API_KEY_HEADER", "X-Traction-Client-Id")

EBI_TAXONOMY_URL = "https://www.ebi.ac.uk/ena/taxonomy/rest/tax-id"

# Options: 'json' or 'binary'
SELECTED_ENCODER_FOR_FEEDBACK_MESSAGE = "binary"

# Validate SSL certificate chain when connecting to https
CERTIFICATES_VALIDATION_ENABLED = True

RABBITMQ_PUBLISH_RETRY_DELAY = 5
RABBITMQ_PUBLISH_RETRIES = 36  # 3 minutes of retries

# In our servers, this will be picked up using deployment project's
# roles/deploy_tol_stack/templates/tol-lab-share/app_config.py.j2 and
# environments/uat/group_vars/tol_swarm_managers.yml
MLWH_ENVIRONMENT_NAME = os.environ.get("MLWH_ENVIRONMENT_NAME", "development")
