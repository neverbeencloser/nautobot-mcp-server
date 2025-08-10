"""Nautobot configuration file."""

from nautobot.core.settings import *  # noqa F401,F403
from nautobot.core.settings_funcs import is_truthy, parse_redis_connection  # noqa F401,F403

REDIS_CACHE = 0
REDIS_CACHE_OPS = 1

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": parse_redis_connection(redis_database=REDIS_CACHE),
        "TIMEOUT": 300,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": os.getenv("NAUTOBOT_REDIS_PASSWORD", ""),
        },
    }
}

CACHEOPS_REDIS = parse_redis_connection(redis_database=REDIS_CACHE_OPS)

# Celery broker URL used to tell workers where queues are located
#
CELERY_BROKER_URL = os.getenv("NAUTOBOT_CELERY_BROKER_URL", parse_redis_connection(redis_database=REDIS_CACHE))

# Database configuration. See the Django documentation for a complete list of available parameters:
#   https://docs.djangoproject.com/en/stable/ref/settings/#databases
#
DATABASES = {
    "default": {
        "NAME": os.getenv("NAUTOBOT_DB_NAME", "nautobot"),  # Database name
        "USER": os.getenv("NAUTOBOT_DB_USER", ""),  # Database username
        "PASSWORD": os.getenv("NAUTOBOT_DB_PASSWORD", ""),  # Database password
        "HOST": os.getenv("NAUTOBOT_DB_HOST", "localhost"),  # Database server
        "PORT": os.getenv("NAUTOBOT_DB_PORT", ""),  # Database port (leave blank for default)
        "CONN_MAX_AGE": int(os.getenv("NAUTOBOT_DB_TIMEOUT", "300")),  # Database timeout
        "ENGINE": os.getenv(
            "NAUTOBOT_DB_ENGINE",
            "django_prometheus.db.backends.postgresql"
            if METRICS_ENABLED  # noqa: F405
            else "django.db.backends.postgresql",
        ),  # Database driver ("mysql" or "postgresql")
    }
}

# Ensure proper Unicode handling for MySQL
#
if DATABASES["default"]["ENGINE"].endswith("mysql"):
    DATABASES["default"]["OPTIONS"] = {"charset": "utf8mb4"}

# This key is used for secure generation of random numbers and strings. It must never be exposed outside of this file.
# For optimal security, SECRET_KEY should be at least 50 characters in length and contain a mix of letters, numbers, and
# symbols. Nautobot will not run without this defined. For more information, see
# https://docs.djangoproject.com/en/stable/ref/settings/#std:setting-SECRET_KEY
SECRET_KEY = os.getenv("NAUTOBOT_SECRET_KEY", "m@1b-tx5(+lb#v32v6h8xr_t32%ups2#hqf95ao)%a%9^25v96")

# Set to True to enable server debugging. WARNING: Debugging introduces a substantial performance penalty and may reveal
# sensitive information about your installation. Only enable debugging while performing testing. Never enable debugging
# on a production system.
#
DEBUG = is_truthy(os.getenv("NAUTOBOT_DEBUG", "False"))

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "normal": {
            "format": "%(asctime)s.%(msecs)03d %(levelname)-7s %(name)s :\n  %(message)s",
            "datefmt": "%H:%M:%S",
        },
        "verbose": {
            "format": "%(asctime)s.%(msecs)03d %(levelname)-7s %(name)-20s %(filename)-15s %(funcName)30s() :\n  %(message)s",
            "datefmt": "%H:%M:%S",
        },
    },
    "handlers": {
        "normal_console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "normal",
        },
        "verbose_console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {"handlers": ["normal_console"], "level": "INFO"},
        "nautobot": {
            "handlers": ["verbose_console" if DEBUG else "normal_console"],
            "level": "DEBUG" if DEBUG else "INFO",
        },
    },
}

# The file path where uploaded media such as image attachments are stored. A trailing slash is not needed.
#
MEDIA_ROOT = os.path.join(NAUTOBOT_ROOT, "media").rstrip("/")  # noqa: F405

# Send anonymized installation metrics when `nautobot-server post_upgrade` command is run.
#
INSTALLATION_METRICS_ENABLED = False

# Enable installed plugins. Add the name of each plugin to the list.
#
PLUGINS = ["nautobot_cloud_models"]

# Plugins configuration settings. These settings are used by various plugins that the user may have installed.
# Each key in the dictionary is the name of an installed plugin and its value is a dictionary of settings.
#
PLUGINS_CONFIG = {}
