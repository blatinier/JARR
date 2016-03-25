#!/usr/bin/env python3
import os
import imp
from sys import argv, stderr, path
root = os.path.join(os.path.dirname(globals()['__file__']), 'src/')
path.append(root)

from lib import conf_handling


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


def build_conf(test=False):
    try:
        import conf
        could_import_conf = True
    except ImportError:
        conf = None
        could_import_conf = False

    for section in conf_handling.SECTIONS:
        section_edit = section.get('edit', True)
        if not test and section_edit and 'ask' in section:
            print()
            section_edit = ask(section['ask'],
                    choices=conf_handling.ABS_CHOICES, default='no')
        prefix = section.get('prefix', '')
        if not test and section_edit and prefix:
            title(prefix)
        for option in section['options']:
            edit = section_edit and option.get('edit', True)

            name = conf_handling.get_key(section, option)

            if test and 'test' in option:
                default = option['test']
            elif could_import_conf and hasattr(conf, name):
                default = getattr(conf, name)
            else:
                default = option.get('default')

            if edit and not test:
                value = ask(option['ask'], choices=option.get('choices', []),
                            default=default)
            else:
                value = default
            if 'type' in option:
                value = option['type'](value)
            yield prefix, name, value


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
    test = '--test' in argv
    conf_handling.write_conf(build_conf(test))
    import conf
    imp.reload(conf)
    install_postgres = 'postgres' in conf.SQLALCHEMY_DATABASE_URI
    install_python_deps(test, install_postgres)


if __name__ == '__main__':
    main()
