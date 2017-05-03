import json

from log import logger

secrets_path = '/secrets/secrets.json'
logger.info("Reading secrets from '%s'" % secrets_path)
with open(secrets_path) as f:
    secrets = json.loads(f.read())
