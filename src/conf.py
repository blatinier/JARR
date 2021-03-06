#! /usr/bin/env python
# -*- coding: utf-8 -*-
""" Program variables.

This file contain the variables used by the application.
"""
import os
import logging

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PATH = os.path.abspath(".")
API_ROOT = '/api/v2.0'

# available languages
LANGUAGES = {
    'en': 'English',
    'fr': 'French'
}

TIME_ZONE = {
    "en": "US/Eastern",
    "fr": "Europe/Paris"
}

ON_HEROKU = int(os.environ.get('HEROKU', 0)) == 1
DEFAULTS = {"platform_url": "",
            "self_registration": "false",
            "cdn_address": "",
            "admin_email": "",
            "postmark_api_key": "",
            "recaptcha_public_key": "",
            "recaptcha_private_key": "",
            "nb_worker": "100",
            "api_login": "",
            "api_passwd": "",
            "google_id": "",
            "google_secret": "",
            "twitter_id": "",
            "twitter_secret": "",
            "facebook_id": "",
            "facebook_secret": "",
            "default_max_error": "3",
            "log_path": "jarr.log",
            "log_level": "info",
            "readability_key": "",
            "user_agent": "",
            "resolve_article_url": "false",
            "secret": "",
            "enabled": "false",
            "notification_email": "",
            "starttls": "true",
            "host": "0.0.0.0",
            "port": "5000",
            "crawling_method": "http",
            "webzine_root": "/tmp",
            }

if not ON_HEROKU:
    try:
        import configparser as confparser
    except:
        import ConfigParser as confparser
    # load the configuration
    config = confparser.SafeConfigParser(defaults=DEFAULTS)
    config.read(os.path.join(BASE_DIR, "conf/conf.cfg"))
else:
    class Config(object):
        def get(self, _, name):
            return os.environ.get(name.upper(), DEFAULTS.get(name))

        def getint(self, _, name):
            return int(self.get(_, name))

        def getboolean(self, _, name):
            value = self.get(_, name)
            if value == 'true':
                return True
            elif value == 'false':
                return False
            return None
    config = Config()


SELF_REGISTRATION = config.getboolean('misc', 'self_registration')
PLATFORM_URL = config.get('misc', 'platform_url')
ADMIN_EMAIL = config.get('misc', 'admin_email')
RECAPTCHA_PUBLIC_KEY = config.get('misc', 'recaptcha_public_key')
RECAPTCHA_PRIVATE_KEY = config.get('misc',
                                    'recaptcha_private_key')
LOG_PATH = os.path.abspath(config.get('misc', 'log_path'))
NB_WORKER = config.getint('misc', 'nb_worker')
API_LOGIN = config.get('crawler', 'api_login')
API_PASSWD = config.get('crawler', 'api_passwd')

SQLALCHEMY_DATABASE_URI = config.get('database', 'database_url')

USER_AGENT = config.get('crawler', 'user_agent')
RESOLVE_ARTICLE_URL = config.getboolean('crawler',
                                        'resolve_article_url')
DEFAULT_MAX_ERROR = config.getint('crawler',
                                  'default_max_error')
ERROR_THRESHOLD = int(DEFAULT_MAX_ERROR / 2)

CRAWLING_METHOD = config.get('crawler', 'crawling_method')

LOG_LEVEL = {'debug': logging.DEBUG,
             'info': logging.INFO,
             'warn': logging.WARN,
             'error': logging.ERROR,
             'fatal': logging.FATAL}[config.get('misc', 'log_level')]

WEBSERVER_HOST = config.get('webserver', 'host')
WEBSERVER_PORT = config.getint('webserver', 'port')
WEBSERVER_SECRET = config.get('webserver', 'secret')

CDN_ADDRESS = config.get('cdn', 'cdn_address')
READABILITY_KEY = config.get('misc', 'readability_key')
OAUTH = {'twitter': {'id': config.get('misc', 'twitter_id'),
                     'secret': config.get('misc', 'twitter_secret')},
         'facebook': {'id': config.get('misc', 'facebook_id'),
                      'secret': config.get('misc', 'facebook_secret')},
         'google': {'id': config.get('misc', 'google_id'),
                    'secret': config.get('misc', 'google_secret')},
         }

NOTIFICATION_EMAIL = config.get('notification', 'notification_email')
NOTIFICATION_HOST = config.get('notification', 'host')
NOTIFICATION_STARTTLS = config.getboolean('notification', 'starttls')
NOTIFICATION_PORT = config.getint('notification', 'port')
NOTIFICATION_USERNAME = config.get('notification', 'username')
NOTIFICATION_PASSWORD = config.get('notification', 'password')
POSTMARK_API_KEY = config.get('notification', 'postmark_api_key')

WEBZINE_ROOT = config.get('webserver', 'webzine_root')
