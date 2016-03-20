#!/usr/bin/env python3
import random
import os.path
import logging
from sys import argv, stderr
from collections import defaultdict


ABS_CHOICES = {'yes': True, 'y': True, 'no': False, 'n': False}
REQUIREMENTS = ['aiohttp==0.21.0',
                'alembic==0.8.4',
                'beautifulsoup4==4.4.1',
                'feedparser==5.2.1',
                'Flask==0.10.1',
                'Flask-Babel==0.9',
                'Flask-Login==0.3.2',
                'Flask-Migrate==1.7.0',
                'Flask-Principal==0.4.0',
                'Flask-RESTful==0.3.5',
                'Flask-Script==2.0.5',
                'Flask-SQLAlchemy==2.1',
                'Flask-SSLify==0.1.5',
                'Flask-WTF==0.12',
                'lxml==3.5.0',
                'opml==0.5',
                'python-dateutil==2.4.2',
                'python-postmark==0.4.7',
                'rauth==0.7.2',
                'requests==2.9.1',
                'requests-futures==0.9.5',
                'SQLAlchemy==1.0.11',
                'WTForms==2.1',
                ]
POSTGRES_REQ = 'psycopg2==2.6.1'
DEV_REQUIREMENTS = ['pep8', 'coverage', 'coveralls']
SECTIONS = (
        {'options': [
            {'key': 'API_ROOT', 'default': '/api/v2.0', 'edit': False},
            {'key': 'LANGUAGES', 'edit': False,
                'default': {'en': 'English', 'fr': 'French'}},
            {'key': 'TIME_ZONE', 'edit': False,
                'default': {'en': 'US/Eastern', 'fr': 'Europe/Paris'}},

            {'key': 'PLATFORM_URL', 'default': 'http://0.0.0.0:5000/',
                'ask': 'At what address will your installation of JARR '
                       'be available'},
            {'key': 'SQLALCHEMY_DATABASE_URI',
                'ask': 'Enter the database URI',
                'default': 'postgres://127.0.0.1:5432/jarr',
                'test': 'sqlite:///:memory:'},
            {'key': 'SQLALCHEMY_TRACK_MODIFICATIONS',
                'edit': False, 'default=': True, 'type': bool},
            {'key': 'SECRET_KEY', 'edit': False,
                'default': str(random.getrandbits(128))},
            {'key': 'ON_HEROKU', 'edit': False, 'default': True, 'type': bool},
        ]},
        {'prefix': 'LOG', 'edit': False, 'options': [
            {'key': 'LEVEL', 'default': 'warn', 'test': 'debug',
                'choices': ('debug', 'info', 'warn', 'error', 'fatal')},
            {'key': 'TYPE', 'default': ''},
            {'key': 'PATH', 'default': ''},
        ]},
        {'prefix': 'CRAWLER', 'edit': False, 'options': [
            {'key': 'LOGIN', 'default': 'admin'},
            {'key': 'PASSWD', 'default': 'admin'},
            {'key': 'NBWORKER', 'type': int, 'default': 2, 'test': 1},
            {'key': 'TYPE', 'default': 'http', 'edit': False},
            {'key': 'RESOLV', 'type': bool, 'default': False,
                'choices': ABS_CHOICES, 'edit': False},
            {'key': 'USER_AGENT',
                'edit': False, 'default': 'https://github.com/jaesivsm/JARR'},
        ]},
        {'prefix': 'PLUGINS', 'options': [
            {'key': 'READABILITY_KEY', 'default': '',
                'ask': 'Enter your readability key if you have one'},
        ]},
        {'prefix': 'AUTH', 'options': [
            {'key': 'ALLOW_SIGNUP', 'default': 'yes', 'type': bool,
                'choices': ABS_CHOICES,
                'ask': 'Do you want to allow people to create account'},
            {'key': 'RECAPTCHA_USE_SSL', 'default': True, 'edit': False},
            {'key': 'RECAPTCHA_PUBLIB_KEY', 'default': '',
                'ask': 'If you have a recaptcha public key enter it'},
            {'key': 'RECAPTCHA_PRIVATE_KEY', 'default': '',
                'ask': 'If you have a recaptcha private key enter it'},
        ]},
        {'prefix': 'OAUTH',
         'ask': 'Do you want to configure third party OAUTH provider',
         'options': [
            {'key': 'ALLOW_SIGNUP', 'default': 'yes', 'type': bool,
                'choices': ABS_CHOICES,
                'ask': 'Do you want to allow people to create account through '
                       'third party OAUTH provider'},
            {'key': 'TWITTER_ID', 'default': '',
                'ask': 'Enter your twitter id if you have one'},
            {'key': 'TWITTER_SECRET', 'default': '',
                'ask': 'Enter your twitter secret if you have one'},
            {'key': 'FACEBOOK_ID', 'default': '',
                'ask': 'Enter your facebook id if you have one'},
            {'key': 'FACEBOOK_SECRET', 'default': '',
                'ask': 'Enter your facebook secret if you have one'},
            {'key': 'GOOGLE_ID', 'default': '',
                'ask': 'Enter your google id if you have one'},
            {'key': 'GOOGLE_SECRET', 'default': '',
                'ask': 'Enter your google secret if you have one'},
        ]},
        {'prefix': 'NOTIFICATION', 'edit': False, 'options': [
            {'key': 'EMAIL', 'default': ''},
            {'key': 'HOST', 'default': 'smtp.googlemail.com'},
            {'key': 'STARTTLS', 'type': bool,
                'default': 'yes', 'choices': ABS_CHOICES},
            {'key': 'PORT', 'type': int, 'default': 587},
            {'key': 'LOGIN', 'default': ''},
            {'key': 'PASSWORD', 'default': ''},
        ]},

        {'prefix': 'FEED', 'edit': False, 'options': [
            {'key': 'ERROR_MAX', 'type': int, 'default': 6, 'edit': False},
            {'key': 'ERROR_THRESHOLD',
                'type': int, 'default': 3, 'edit': False},
            {'key': 'REFRESH_RATE',
                'default': 60, 'type': int, 'edit': False},
        ]},
        {'prefix': 'WEBSERVER', 'edit': False, 'options': [
            {'key': 'HOST', 'default': '0.0.0.0', 'edit': False},
            {'key': 'PORT', 'default': 5000, 'type': int, 'edit': False},
        ]},
)


def title(text):
    line = '#' * (len(text) + 4)
    print('\n%s\n# %s #\n%s' % (line, text, line))


def ask(text, choices=[], default=None, cast=None):
    while True:
        print(text, end=' ')
        if choices:
            print('[%s]' % '/'.join([chc.upper() if chc == default else chc
                                     for chc in choices]), end=' ')
        if default:
            print('(default: %r)' % default, end=' ')
        print(':', end=' ')

        result = input().lower()
        if not result and default is None:
            print('you must provide an answer')
        elif result and choices and result not in choices:
            print('%r is not in %r' % (result, choices))
        elif not result and default is not None:
            if isinstance(choices, dict):
                return choices[default]
            return default
        elif result:
            if isinstance(choices, dict):
                return choices[result]

            if cast is not None:
                try:
                    result = cast(result)
                except ValueError:
                    print("Couldn't cast %r to %r" % (result, cast))
                    continue
            return result


def build_conf(values, test=False):
    for section in SECTIONS:
        section_edit = section.get('edit', True)
        if not test and section_edit and 'ask' in section:
            print()
            section_edit = ask(section['ask'],
                    choices=ABS_CHOICES, default='no')
        if not test and section_edit and section.get('prefix'):
            title(section['prefix'])
        if section.get('prefix'):
            yield '\n'
            yield '# %s\n' % section['prefix']
        for option in section['options']:
            edit = section_edit and option.get('edit', True)
            if test and 'test' in option:
                default = option['test']
            else:
                default = option.get('default')
            name = section.get('prefix', '')
            if name:
                name += '_'
            name += option['key']
            if edit and not test:
                value = ask(option['ask'], choices=option.get('choices', []),
                            default=default)
            else:
                value = default
            if 'type' in option:
                value = option['type'](value)
            values[name] = value
            yield '%s = %r\n' % (name, value)


def write_conf(conf):
    with open('./src/conf.py', 'w') as fd:
        fd.writelines(conf)


def install_python_deps(test, install_postgres):
    try:
        import pip
    except ImportError:
        print('pip is not available ; aborting', file=stderr)

    pip.main(['install', '--upgrade'] + REQUIREMENTS)
    if install_postgres:
        pip.main(['install', '--upgrade', POSTGRES_REQ])
    if test:
        pip.main(['install', '--upgrade'] + DEV_REQUIREMENTS)


def main():
    values, test = {}, '--test' in argv
    write_conf(build_conf(values, test))
    install_postgres = 'postgres' in values['SQLALCHEMY_DATABASE_URI']
    install_python_deps(test, install_postgres)


if __name__ == '__main__':
    main()
