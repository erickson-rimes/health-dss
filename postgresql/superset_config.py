from custom_sso_security_manager import OIDCSecurityManager
from flask_appbuilder.security.manager import AUTH_OID, AUTH_REMOTE_USER, AUTH_DB, AUTH_LDAP, AUTH_OAUTH
import os

AUTH_TYPE = AUTH_OID
SECRET_KEY= 'SomethingNotEntirelySecret'
OIDC_CLIENT_SECRETS =  '/app/pythonpath/client_secret.json'
OIDC_ID_TOKEN_COOKIE_SECURE = False
OIDC_OPENID_REALM= 'CRISH'
OIDC_INTROSPECTION_AUTH_METHOD= 'client_secret_post'

CUSTOM_SECURITY_MANAGER = OIDCSecurityManager

# Will allow user self registration, allowing to create Flask users from Authorized User
AUTH_USER_REGISTRATION = True

AUTH_ROLES_MAPPING = {
    "pgadmin": ["Gamma","Alpha"],
}

# The default user self registration role
AUTH_USER_REGISTRATION_ROLE = 'Public'