from zoneinfo import ZoneInfo

from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = [
    'BaseConfigSettings',
    'LOGGING_CONFIG',
    'application_settings',
    'postgres_settings',
    'matching_settings',
    'parser_settings',
]


class BaseConfigSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')


class ApplicationSettings(BaseConfigSettings):
    APP_TITLE: str = 'templateproject'
    APP_VERSION: str = '0.0.1'
    APP_DEBUG: bool = False
    APP_TELEGRAM_CHANNEL: str = ''
    APP_TELEGRAM_REVIEWS_GROUP: int = 0
    APP_TELEGRAM_KEY: str = ''
    APP_BOT_ID: str = 'flcd_test_bot'
    APP_DEFAULT_USER_ID: int = 0
    APP_PROMETHEUS_HOST: str = '0.0.0.0'
    APP_PROMETHEUS_PORT: int = 8000
    APP_TIMEZONE: ZoneInfo = ZoneInfo('Europe/Moscow')


class ParserSettings(BaseConfigSettings):
    PARSER_DEFAULT_USER_ID: int = 0
    PARSER_DEFAULT_USER_NAME: str = ''
    PARSER_UPDATE_TIME: int = 300
    PARSER_LOCATION: str = 'msk'
    PARSER_TIMEZONE: ZoneInfo = ZoneInfo('Europe/Moscow')

    TG_API_ID: int = -1
    TG_API_HASH: str = ''
    OPENAI_API_KEY: str = ''


class MatchingSettings(BaseConfigSettings):
    WINDOW_SIZE: int = 1000  # TODO: Change name to MATCHING_WINDOW_SIZE
    BATCH_SIZE: int = 5  # TODO: Change name to MATCHING_BUFFER_SIZE


class PostgresDBSettings(BaseConfigSettings):
    POSTGRES_URI: str = 'None'


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'color': {
            '()': 'colorlog.ColoredFormatter',
            'format': '%(log_color)s[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'log_colors': {
                'DEBUG': 'cyan',
                'INFO': 'green',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'bold_red',
            },
        },
        'standard': {
            'format': '[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'color',
            'level': 'DEBUG',
        },
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'logs/app.log',
            'when': 'D',
            'interval': 1,
            'backupCount': 7,
            'encoding': 'utf-8-sig',
            'formatter': 'standard',
            'level': 'INFO',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'aiohttp.access': {
            'level': 'WARNING',
            'handlers': ['console', 'file'],
            'propagate': False,
        },
    },
}

application_settings = ApplicationSettings()

parser_settings = ParserSettings()

postgres_settings = PostgresDBSettings()

matching_settings = MatchingSettings()
