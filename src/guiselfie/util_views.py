import logging, json
from flask_login import current_user
from flask_security import url_for_security
from flask import request, redirect, Response, render_template
from functools import wraps
from .util_users import is_user_admin

def log_access():
    logger = logging.getLogger('selfie.main')
    msg = "%s (%s) requested from %s to %s %s" % (
            current_user.name, current_user.email, request.remote_addr, request.method, request.url)
    params = ""
    for k in (request.form.keys()):
        val = request.form.get(k)
        if k.lower()=="password":
            val = ""
        params += " \"%s\" \"%s\"" % (k, val)
    if params:
        msg = "%s, request parameters %s" % (msg, params)
    logger.info(msg)

def view_wrapper(IsView=True, AdminRequired=False):
    def outer(fn):
        @wraps(fn)
        def authenticate_and_log(*args, **kwargs):
            if not current_user.is_authenticated:
                if IsView:
                    return redirect(url_for_security('login', next=request.path))
                else:
                    return Response(json.dumps({"Error": "Unauthorized"}), status=401, mimetype='application/json')
            if AdminRequired and not is_user_admin():
                if IsView:
                    return render_template('error/403.html'), 403
                else:
                    return Response(json.dumps({"Error": "Forbidden"}), status=403, mimetype='application/json')
            log_access()
            return fn(*args, **kwargs)
        return authenticate_and_log
    return outer
