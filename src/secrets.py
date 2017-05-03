import json

secrets_path = '/secrets/secrets.json'
print("Reading secrets from '%s'" % secrets_path)
with open(secrets_path) as f:
    secrets = json.loads(f.read())
