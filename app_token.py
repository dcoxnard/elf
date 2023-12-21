import os

from itsdangerous import URLSafeTimedSerializer
from itsdangerous.exc import BadSignature, SignatureExpired, BadTimeSignature


# TODO: Obviously this needs to be improved
# https://www.freecodecamp.org/news/setup-email-verification-in-flask-app/
secret_key = os.environ["APP_SECRET_KEY"]
salt = os.environ["APP_SALT"]


def generate_token(email):
    serializer = URLSafeTimedSerializer(secret_key)
    token = serializer.dumps(email, salt)
    return token


def validate_token(token, expiration=3600):
    """
    :param token: str
    :param expiration: int
    :return: Optional[Email] -- None if validation fails; email otherwise
    """
    serializer = URLSafeTimedSerializer(secret_key)
    try:
        email = serializer.loads(token, salt=salt, max_age=expiration)
    except (BadSignature, BadTimeSignature, SignatureExpired):
        retval = None
    else:
        retval = email

    return retval
