import os

MAJOR_RELEASE = "1"
MINOR_RELEASE = "0"
BUILD = "9518"

SECRET_KEY=os.urandom(24)

MYSQL_DATABASE_HOST='localhost'
MYSQL_DATABASE_DB='selfie'
MYSQL_DATABASE_USER='nocadmin'
MYSQL_DATABASE_PASSWORD='Syltetoy345'
MYSQL_DATABASE_SOCKET=False
SQLALCHEMY_DATABASE_URI='mysql://%s:%s@%s/%s' % (MYSQL_DATABASE_USER, MYSQL_DATABASE_PASSWORD, MYSQL_DATABASE_HOST, MYSQL_DATABASE_DB)
SQLALCHEMY_TRACK_MODIFICATIONS=False

DEBUG=True
SECURITY_REGISTERABLE=False
SECURITY_RECOVERABLE=True
SECURITY_CONFIRMABLE=False

SECURITY_PASSWORD_HASH='pbkdf2_sha512'
SECURITY_PASSWORD_SALT="xqkatsju4dauk4so8nvq8uc2"
SECURITY_TRACKABLE=True
SECURITY_RESET_PASSWORD_WITHIN='5 minutes'
SECURITY_EMAIL_SUBJECT_PASSWORD_RESET='[Selfie.VC] Password reset requested'
SECURITY_EMAIL_SUBJECT_PASSWORD_NOTICE='[Selfie.VC] Password reset completed'

QOS_VC_SUPPORT="support@selfie.vc"
SECURITY_MSG_INVALID_EMAIL_ADDRESS=("Invalid email address.", "error")
SECURITY_MSG_TOO_MANY_FAILED_LOGINS=("Too many failed logins, please email %s to reset password." % QOS_VC_SUPPORT, "error")
SECURITY_MSG_FAILD_TO_SEND_PASSWORD_RESET_EMAIL=("Failed to send password reset email, please contact %s." % QOS_VC_SUPPORT, "error")
SECURITY_MSG_INVALID_RESET_PASSWORD_TOKEN=("Password reset token has expired, please re-enter email address.", "error")

# enable this for testing only
WTF_CSRF_ENABLED=False

MAIL_DEFAULT_SENDER = 'no-reply@nocportal.mnsbone.net'

from pathlib import Path
SELFIE_CONFIG_DIR = str(Path(Path(__file__).parent.absolute()))
LOGGING_CFG = "%s/logging_prod.conf" % SELFIE_CONFIG_DIR
