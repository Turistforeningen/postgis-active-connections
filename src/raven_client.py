from raven import Client

from secrets import secrets

print("Initializing raven")
client = Client(secrets['RAVEN_DSN'])
