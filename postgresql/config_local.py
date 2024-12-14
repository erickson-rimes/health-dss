# import os

OAUTH2_CONFIG = [
    {
        'OAUTH2_NAME': 'CRISH',
        'OAUTH2_DISPLAY_NAME': 'CRISH',
        'OAUTH2_CLIENT_ID': 'pgadmin-client',
        'OAUTH2_CLIENT_SECRET': '3OXfP5deg4uRYZALvEl1vktNKyTy2Tyc',
        'OAUTH2_TOKEN_URL': 'http://10.227.203.244:8051/realms/CRISH/protocol/openid-connect/token',
        'OAUTH2_AUTHORIZATION_URL': 'http://10.227.203.244:8051/realms/CRISH/protocol/openid-connect/auth',
        'OAUTH2_API_BASE_URL': 'http://10.227.203.244:8051',
        'OAUTH2_USERINFO_ENDPOINT': 'http://10.227.203.244:8051/realms/CRISH/protocol/openid-connect/userinfo',
        'OAUTH2_SERVER_METADATA_URL': 'http://10.227.203.244:8051/realms/CRISH/.well-known/openid-configuration',
        'OAUTH2_SCOPE': 'openid profile address roles email phone',
        'OAUTH2_ADDITIONAL_CLAIMS': {'roles': 'pgadmin'},
        'OAUTH2_ICON': 'fa-lock',
        'OAUTH2_BUTTON_COLOR': '#000000',
        'OAUTH2_SSL_CERT_VERIFICATION': False,
        'NODE_BLACKLIST': ['Casts', 'Aggregates']
    }
]