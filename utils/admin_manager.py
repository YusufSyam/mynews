import functools
from flask import session, redirect, url_for, request
from bson import ObjectId
from .db_class import *

def login_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return func(*args, **kwargs)

    return secure_function

def guess_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        if "user_id" in session:
            return redirect(url_for("admin_dashboard"))
        return func(*args, **kwargs)

    return secure_function

def admin_required(func):
    @functools.wraps(func)
    def secure_function(*args, **kwargs):
        user= Writer.objects(pk=session.get('user_id')).first()
        if user.authority != 'admin':
            # TODO FLASH
            return redirect(url_for("admin_dashboard"))
        return func(*args, **kwargs)

    return secure_function

def check_user(username, password):
    user = Writer.objects(username= username).first()
    if user:
        if user.password == password:
            return True
    return False

def is_logged_in():
    return 'user_id' in session

def current_user():
    if 'user_id' in session:
        return Writer.objects(pk=ObjectId(session['user_id'])).first()
    else:
        return False

def logged_user_is_admin():
    return True if current_user().authority == 'admin' else False

def logged_user_is_user(user_id):
    return True if current_user().pk==user_id else False
