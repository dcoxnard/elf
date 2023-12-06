from itsdangerous import URLSafeTimedSerializer
from itsdangerous.exc import BadSignature, SignatureExpired, BadTimeSignature


mock_secret_key = ":)"
mock_salt = ":)"


def generate_token(email):
    serializer = URLSafeTimedSerializer(mock_secret_key)
    token = serializer.dumps(email, mock_salt)
    return token


def validate_token(token, expiration=3600):
    """
    :param token:
    :param expiration:
    :return: Optional[Email] -- None if validation fails; email otherwise
    """
    serializer = URLSafeTimedSerializer(mock_secret_key)
    try:
        email = serializer.loads(token, salt=mock_salt, max_age=expiration)
    except (BadSignature, BadTimeSignature, SignatureExpired):
        retval = None
    else:
        retval = email

    return retval
