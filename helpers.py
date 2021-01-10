# I have took an inspiration from CS50 ProblemSet no.8. Thank you for that CS50 team !

import os

from flask import redirect, session, render_template
from functools import wraps

def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

# error message function
def error(text):
    return render_template("error.html", text=text)
