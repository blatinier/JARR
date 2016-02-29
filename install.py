from sys import stderr


def ask(text, choices=[], default=None):
    while True:
        print(text, end=' ')
        if choices:
            print('[%s]' % '/'.join([chc.upper() if chc == default else chc
                                     for chc in choices]), end=' ')
        if default:
            print('(default: %r)' % default, end=' ')
        result = input()
        if not result and not default:
            print('you must provide an answer')
        elif result and choices and result not in choices:
            print('%r is not in %r' % (result, choices))
        elif not result and default:
            if isinstance(choices, dict):
                return choices[default]
            return default
        elif result:
            if isinstance(choices, dict):
                return choices[result]
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
    conf = {'main': {}}
    abs_choices = {'yes': True, 'y': True, 'no': False, 'n': False}
    conf['main']['url'] = ask('What will be the url ?',
                              default='http://0.0.0.0:5000')
    conf['admin_login'] = ask('Your admin login')
    conf['admin_password'] = ask('Your admin password')
    if ask('Do you have a readability API key ?', abs_choices, default='No'):
        conf['plugins']['readability'] = ask('Enter your key')
    for plugin in ['google', 'twitter', 'facebook']:
        if ask('Do you have a %s API key ?' % plugin.capitalize(),
                abs_choices, default='No'):
            conf['plugins'][plugin]['id'] = ask('Enter id')
            conf['plugins'][plugin]['secret'] = ask('Enter id')
    conf['notifications']['email'] \
            = ask("The mail with which we'll send (few) nofitications")
    conf['notifications']['password'] = ask("The smtp password")
    conf['notifications']['host'] = ask("The host",
            default="smtp.googlemail.com")
    conf['notifications']['port'] = ask("The port", default=587)
    conf['notifications']['starttls'] = ask("Use starttls",
            choices={True: True, False: False}, default=True)
    return conf


if __name__ == '__main__':
    build_conf()
    install_python_deps()
