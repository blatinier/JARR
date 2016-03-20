import json
import logging

from werkzeug.exceptions import NotFound
from flask import (render_template, flash, session, request,
                   url_for, redirect, current_app)
from flask.ext.babel import gettext
from flask.ext.login import LoginManager, logout_user, \
                            login_required, current_user
from flask.ext.principal import (Principal, AnonymousIdentity, UserNeed,
                                 identity_changed, identity_loaded,
                                 session_identity_loader)

import conf
from web.views.common import admin_role, api_role, login_user_bundle
from web.controllers import UserController
from web.forms import SignupForm, SigninForm
from rauth import OAuth1Service, OAuth2Service

Principal(current_app)
# Create a permission with a single Need, in this case a RoleNeed.

login_manager = LoginManager()
login_manager.init_app(current_app)
login_manager.login_view = 'login'

logger = logging.getLogger(__name__)


@identity_loaded.connect_via(current_app._get_current_object())
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user

    # Add the UserNeed to the identity
    if current_user.is_authenticated:
        identity.provides.add(UserNeed(current_user.id))
        if current_user.is_admin:
            identity.provides.add(admin_role)
        if current_user.is_api:
            identity.provides.add(api_role)


@login_manager.user_loader
def load_user(user_id):
    return UserController(user_id, ignore_context=True).get(
            id=user_id, is_active=True)


# FROM http://blog.miguelgrinberg.com/post/oauth-authentication-with-flask
class OAuthSignIn:  # pragma: no cover
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        self.consumer_id = getattr(conf, ('OAUTH_%s_ID' % provider_name).upper)
        self.consumer_secret \
                = getattr(conf, ('OAUTH_%s_SECRET' % provider_name).upper)

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return url_for('oauth_callback', provider=self.provider_name,
                       _external=True)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]


class GoogleSignIn(OAuthSignIn):  # pragma: no cover
    def __init__(self):
        super().__init__('google')
        self.service = OAuth2Service(
                name='google',
                client_id=self.consumer_id,
                client_secret=self.consumer_secret,
                base_url='https://www.googleapis.com/oauth2/v1/',
                access_token_url='https://accounts.google.com/o/oauth2/token',
                authorize_url='https://accounts.google.com/o/oauth2/auth'
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(scope='email',
                response_type='code', redirect_uri=self.get_callback_url()))

    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
                data={'code': request.args['code'],
                      'grant_type': 'authorization_code',
                      'redirect_uri': self.get_callback_url()},
                decoder=lambda x: json.loads(x.decode('utf8')),

        )
        info = oauth_session.get('userinfo').json()
        return info['id'], info.get('name'), info.get('email')


class TwitterSignIn(OAuthSignIn):  # pragma: no cover
    def __init__(self):
        super().__init__('twitter')
        self.service = OAuth1Service(
            name='twitter',
            consumer_key=self.consumer_id,
            consumer_secret=self.consumer_secret,
            request_token_url='https://api.twitter.com/oauth/request_token',
            authorize_url='https://api.twitter.com/oauth/authorize',
            access_token_url='https://api.twitter.com/oauth/access_token',
            base_url='https://api.twitter.com/1.1/'
        )

    def authorize(self):
        request_token = self.service.get_request_token(
            params={'oauth_callback': self.get_callback_url()}
        )
        session['request_token'] = request_token
        return redirect(self.service.get_authorize_url(request_token[0]))

    def callback(self):
        request_token = session.pop('request_token')
        if 'oauth_verifier' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            request_token[0],
            request_token[1],
            data={'oauth_verifier': request.args['oauth_verifier']}
        )
        info = oauth_session.get('account/verify_credentials.json').json()
        social_id = 'twitter$' + str(info.get('id'))
        login = info.get('screen_name')
        return social_id, login, None


class FacebookSignIn(OAuthSignIn):  # pragma: no cover
    def __init__(self):
        super().__init__('facebook')
        self.service = OAuth2Service(
            name='facebook',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://graph.facebook.com/oauth/authorize',
            access_token_url='https://graph.facebook.com/oauth/access_token',
            base_url='https://graph.facebook.com/'
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': 'authorization_code',
                  'redirect_uri': self.get_callback_url()}
        )
        info = oauth_session.get('me?fields=id,email').json()
        # Facebook doesn't provide login, so the email is used
        return ('facebook$' + info['id'],
                info.get('email').split('@')[0], info.get('email'))


@current_app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = SigninForm()
    if form.validate_on_submit():
        login_user_bundle(form.user)
        return form.redirect('home')
    return render_template('login.html', form=form)


@current_app.route('/logout')
@login_required
def logout():
    # Remove the user information from the session
    logout_user()

    # Remove session keys set by Flask-Principal
    for key in ('identity.name', 'identity.auth_type'):
        session.pop(key, None)

    # Tell Flask-Principal the user is anonymous
    identity_changed.send(current_app, identity=AnonymousIdentity())
    session_identity_loader()

    return redirect(url_for('login'))


@current_app.route('/signup', methods=['GET', 'POST'])
def signup():
    if not conf.SELF_REGISTRATION:
        flash(gettext("Self-registration is disabled."), 'warning')
        return redirect(url_for('home'))
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = SignupForm()
    if form.validate_on_submit():
        user = UserController().create(login=form.login.data,
                email=form.email.data, password=form.password.data)
        login_user_bundle(user)
        return redirect(url_for('home'))

    return render_template('signup.html', form=form)


@current_app.route('/oauth/authorize/<provider>')
def oauth_authorize(provider):  # pragma: no cover
    return OAuthSignIn.get_provider(provider).authorize()


@current_app.route('/oauth/callback/<provider>')
def oauth_callback(provider):  # pragma: no cover
    if not current_user.is_anonymous:
        return redirect(url_for('home'))
    oauth = OAuthSignIn.get_provider(provider)
    social_id, username, email = oauth.callback()
    if social_id is None:
        flash('Authentication failed.')
        return redirect(url_for('home'))
    ucontr = UserController()
    try:
        user = ucontr.get(**{'%s_identity' % provider: social_id})
    except NotFound:
        user = None
    if not user:
        user = ucontr.create(**{'%s_identity' % provider: social_id,
                                'login': username, 'email': email})
    login_user_bundle(user)
    return redirect(url_for('home'))
