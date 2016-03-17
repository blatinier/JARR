import logging
from collections import defaultdict

def to_log_level(level):
    return {'debug': logging.DEBUG,
            'info': logging.INFO,
            'warn': logging.WARN,
            'error': logging.ERROR,
            'fatal': logging.FATAL}.get(str(level).lower(), logging.WARN)


OPTIONS = (
        {'key': 'api_root', 'default': '/api/v2.0', 'edit': False},
        {'key': 'languages', 'edit': False,
            'default': {'en': 'English', 'fr': 'French'}},
        {'key': 'time_zone', 'edit': False,
            'default': {'en': 'US/Eastern', 'fr': 'Europe/Paris'}},

        {'key': 'platform_url', 'default': 'http://0.0.0.0:5000',
            'help': 'At what address will JARR be available'},
        {'key': 'sqlalchemy_database_uri'},
        {'key': 'default_max_error', 'type': int, 'default': 6, 'edit': False},
        {'key': 'error_threshold', 'type': int, 'default': 3, 'edit': False},
        {'key': 'webserver.host'},
        {'key': 'webserver.port', 'type': int},
        {'key': 'webserver.secret'},

        {'key': 'log.level', 'type': to_log_level,
            'default': 'warn', 'test': 'debug'},
        {'key': 'log.type', 'default': ''},
        {'key': 'log.path', 'default': ''},

        {'key': 'crawler.login', 'default': 'admin'},
        {'key': 'crawler.passwd', 'default': 'admin'},
        {'key': 'crawler.nb_worker', 'type': int, 'default': 2, 'test': 1},
        {'key': 'crawler.type', 'default': 'http', 'edit': False},
        {'key': 'crawler.resolve_article_url', 'type': bool, 'default': False},
        {'key': 'crawler.user_agent',
                'default': 'https://github.com/jaesivsm/JARR'},

        {'key': 'readability_key'},
        {'key': 'auth.allow_signup', 'default': True, 'type': bool},
        {'key': 'auth.recaptcha_public_key'},
        {'key': 'auth.recaptcha_private_key'},
        {'key': 'oauth.allow_signup', 'default': True, 'type': bool},
        {'key': 'oauth.twitter.id'},
        {'key': 'oauth.twitter.secret'},
        {'key': 'oauth.facebook.id'},
        {'key': 'oauth.facebook.secret'},
        {'key': 'oauth.google.id'},
        {'key': 'oauth.google.secret'},

        {'key': 'notification.email'},
        {'key': 'notification.host'},
        {'key': 'notification.starttls'},
        {'key': 'notification.port'},
        {'key': 'notification.login'},
        {'key': 'notification.password'},
)


class Config:

    def __init__(self, options, test=False):
        self.__options = options
        self.__test = test

    def __browse_keys(self):
        for option in self.__options:
            yield option['key'].replace('.', '_').upper()

    def _dump(self):
        def defaultdict_factory():
            return defaultdict(defaultdict_factory)
        to_dump = defaultdict(defaultdict_factory)
        for option in self.__options:
            if getattr(self, option['key'], None):
                value = getattr(self, option['key'])
            elif self.__test and 'test' in option:
                value = option['test']
            elif 'default' in option:
                value = option['default']
            else:
                value = None
            if '.' in option['key']:
                tmp_d = to_dump
                for sub_key in option['key'].split('.'):
                    if not option['key'].endswith(sub_key):  # skiping last one
                        tmp_d = to_dump[sub_key]
                tmp_d[option['key'].split('.')[-1]] = value
            else:
                to_dump[option['key']] = value
        return to_dump
