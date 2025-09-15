from flask import redirect, render_template, session
from functools import warps

def login_required(f):
    @warps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") ==  None:
            return redirect("/login")
        return f(*args, **kwargs)
    
    return decorated_function