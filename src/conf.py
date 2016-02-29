#! /usr/bin/env python
# -*- coding: utf-8 -*-
""" Program variables.

This file contain the variables used by the application.
"""
import os
import logging

API_ROOT = '/api/v2.0'
LANGUAGES = {'en': 'English', 'fr': 'French'}
TIME_ZONE = {'en': 'US/Eastern', 'fr': 'Europe/Paris'}

ON_HEROKU = int(os.environ.get('HEROKU', 0)) == 1

config = None  # for now

SELF_REGISTRATION = config.getboolean('misc', 'self_registration')
PLATFORM_URL = config.get('misc', 'platform_url')
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
