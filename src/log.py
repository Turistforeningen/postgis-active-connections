import logging.config

logconfig = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': ('pgac: %(asctime)s %(levelname)-8s %(name)s: '
                       '%(message)s'),
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
        'papertrail': {
            'class': 'logging.handlers.SysLogHandler',
            'formatter': 'default',
            'address': ('logs3.papertrailapp.com', 30847),
        },
    },
    'root': {
        'handlers': ['console', 'papertrail'],
        'level': 'DEBUG',
    }
}

logging.config.dictConfig(logconfig)

logger = logging.getLogger('pgac')
