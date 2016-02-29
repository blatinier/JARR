#!/usr/bin/env python3
import random
import os.path
from sys import stderr
from collections import defaultdict


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


def parse_requirements(filename):
    with open(filename) as fd:
        for line in fd.readlines():
            yield line.strip()


def install_python_deps():
    try:
        import pip
    except ImportError:
        print('pip is not available ; aborting', file=stderr)
    pip.main(['install', '--upgrade']
             + list(parse_requirements('../requirements.txt')))


def build_conf():
    def defaultdict_factory():
        return defaultdict(defaultdict_factory)
    conf = defaultdict(defaultdict_factory,
            {'web': {'secret': random.getrandbits(128)},
             'default_max_error': 6, 'error_threshold': 3,
             'crawler': {'nb_worker': 6,
                         'user_agent': 'https://github.com/jaesivsm/JARR'}})
    abs_choices = {'yes': True, 'y': True, 'no': False, 'n': False}

    title('Basic configuration')
    conf['url'] = ask('What will be the url', default='http://0.0.0.0:5000')
    adm_login = conf['crawler']['login'] = ask('Your admin login')
    adm_pass = conf['crawler']['password'] = ask('Your admin password')
    conf['logpath'] = ask('Logpath (empty will mean Syslog)', default='')

    title('Configuration of the web application')
    conf['web']['self_registration'] = ask('Do you allow auto registration',
                                           choices=abs_choices, default='no')
    db_type = ask('What kind of db engine will you use',
                  choices=['sqlite', 'postgresql'], default='sqlite')
    if db_type == 'postgresql':
        db_addr = ask('Enter db address', default='127.0.0.1')
        db_port = ask('Enter db port', default=5432, cast=int)
        db_name = ask('Enter db name')
        db_login = ask('Enter db login')
        db_passwd = ask('Enter db password')
        conf['database'] = 'postgres://%s:%s@%s:%s/%s' % (db_login, db_passwd,
                db_addr, db_port, db_name)
    else:
        db_loc = ask('Enter db location', default='jarr.db')
        conf['database'] = "sqlite+pysqlite://%s" % os.path.abspath(db_loc)

    title('Sign up options')
    conf['plugins']['recaptcha_pub'] = ask('Recaptcha public key', default='')
    conf['plugins']['recaptcha_private'] \
            = ask('Recaptcha private key', default='')
    if ask('Do you have a readability API key', abs_choices, default='no'):
        conf['plugins']['readability'] = ask('Enter your key')
    for plugin in ['google', 'twitter', 'facebook']:
        if ask('Do you have a %s API key' % plugin.capitalize(),
                abs_choices, default='no'):
            conf['plugins'][plugin]['id'] = ask('Id')
            conf['plugins'][plugin]['secret'] = ask('Secret')
    title('Notifications configuration')
    conf['notifications']['email'] \
            = ask("The mail with which we'll send (few) nofitications")
    conf['notifications']['password'] = ask("The smtp password")
    conf['notifications']['host'] = ask("The host",
            default="smtp.googlemail.com")
    conf['notifications']['port'] = ask("The port", default=587, cast=int)
    conf['notifications']['starttls'] = ask("Use starttls",
            choices=abs_choices, default='yes')

    if ask('Do you want to configure more advanced options ?',
            choices=abs_choices, default='no'):
        conf['default_max_error'] = ask('How many errors should the '
                'fetching of a field encounters before desactivating it',
                default=conf['default_max_error'], cast=int)
        conf['error_threshold'] = ask('How many errors before marking it as '
                '"in error" to the user',
                default=int(conf['default_max_error'] / 2), cast=int)
        conf['crawler']['nb_worker'] = ask('How many threads should the '
                'crawler use', default=conf['crawler']['nb_worker'])
    print(repr(conf))
    import ipdb
    ipdb.set_trace()
    return conf


if __name__ == '__main__':
    build_conf()
