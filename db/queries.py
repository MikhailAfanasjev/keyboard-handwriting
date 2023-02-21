from db.models import *


def get_user(password):
    return session.query(User).filter_by(password=password).first()


def get_all_users():
    return session.query(User).filter_by().all()


def new_user(password, vector_min, vector_max):
    user = get_user(password)
    if user is None:
        user = User(
            password=password,
            vector_max=vector_max,
            vector_min=vector_min,
        )
        user.save()
    return user
