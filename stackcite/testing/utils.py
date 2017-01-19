from stackcite import data


def make_user(email, password=None, clean=True, save=False):
    user = data.User(email=email)
    if password:
        user.set_password(password)
    if save:
        user.save()
    return user


def make_auth_token(user, clean=True, save=False):
    token = data.AuthToken(_user=user)
    if save:
        token.save()
    return token


def make_conf_token(user, clean=True, save=False):
    token = data.ConfirmToken(_user=user)
    if save:
        token.save()
    return token
