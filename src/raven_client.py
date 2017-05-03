from raven import Client

from log import logger
from secrets import secrets

logger.info("Initializing raven")
client = Client(secrets['RAVEN_DSN'])
