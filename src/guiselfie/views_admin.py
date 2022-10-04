from flask import request, jsonify, Response, Blueprint
from flask_security import login_required
from flask_security import utils as flask_security_utils
import json
from selfie import mysql
from .util_views import view_wrapper
from .util_users import is_user_admin, password_errors

mod_admin = Blueprint('admin', __name__, url_prefix='/admin', template_folder="templates")

def add_user(request, db):
    vals = {}
    for k in ['email', 'name', 'password', 'company_id', 'admin']:
        if k!="admin" and not k in request.form.keys()\
            or (k=="email" or k=="password") and len(request.form.get(k).strip())==0:
            return [400, "Please provide a valid value for {}".format(k)]
        # don't strip space from password
        # add password rule check
        if k=="password":
            vals[k] = request.form.get(k)
            if password_errors(vals['password']):
                return [400, "Password does not satisfy requirements"] 
        if k=="email" or k=='name':
            try:
                vals[k] = request.form.get(k).strip()
            except Exception as e: 
                return [400, "Error parsing value for {}, {}".format(k, str(e))] 
        if k=='admin' or k=='company_id':
            if k=="admin" and not k in request.form.keys():
                vals[k] = 0
            else:
                try:
                    vals[k] = int(request.form.get(k).strip())
                except Exception as e: 
                    return [400, "Error parsing value for {}, {}".format(k, str(e))]

    encrypted_password = flask_security_utils.encrypt_password(vals['password'])

    sql = "insert into user (email, password, name, admin, company_id, active) values ("
    sql += "\"%s\", \"%s\", \"%s\", %d, %d, %d)" % (
            vals["email"],
            encrypted_password,
            vals["name"],
            vals["admin"],
            vals["company_id"],
            1)
    try:
        db.cursor().execute(sql)
        db.commit()
    except Exception as e:
        return [500, "Error modify user ({}) to database, {}".format(userid, str(e))]
    return [None, None]


def update_user(request, db):
    if not 'id' in request.form.keys():
        return [400, "Please provide a valid user id"]
    try:
        userid = int(request.form.get('id').strip())
    except:
        return [400, "Please provide a valid user id"]

    sql = "update user" 
    keys = ['email', 'name', 'password', 'company_id', 'admin']
    i = 0
    isSet = False
    valid = True
    while i < len(keys):
        k = keys[i]
        if not k in request.form.keys():
            i += 1
            continue
        val = request.form.get(k)
        if (k=='email' and len(val.strip())==0) or (k=='password' and password_errors(val)):
            valid = False 
        if k=='id' or k=='company_id' or k=='admin':
            try:
                val = int(val.strip())
            except Exception as e:
                valid = False
        if k=='password':
            val = flask_security_utils.encrypt_password(val)
        if not isSet:
            sql += " set %s=" % k
            isSet = True
        else:
            sql += " %s=" % k
        if isinstance(val, int):
            sql += "%d" % val
        elif isinstance(val, str):
            sql += "\"%s\"" % val
        sql += ","
        i += 1
    if not valid:
        return [400, "Invalid user parameter detected"]
    if isSet:
        sql = sql[:-1]
    sql += " where id=%d" % userid
    try:
        db.cursor().execute(sql)
        db.commit()
    except Exception as e:
        return [500, "Error modify user ({}) to database, {}".format(userid, str(e))]
    return [None, None]

@mod_admin.route('/api/user', methods=['POST', 'PATCH'])
@view_wrapper(IsView=False, AdminRequired=True)
def user_man():
    db = mysql.connect()
    if not is_user_admin():
        return Response(json.dumps({"Error": "Unauthorized"}), status=403, mimetype='application/json')

    if request.method=="POST":
        errcode, err = add_user(request, db)
        if not errcode:
            return jsonify(result="User successfully added")
    elif request.method=="PATCH":
        errcode, err = update_user(request, db)
        if not errcode:
            return jsonify(result="User successfully modified")
    if errcode:
        return Response(json.dumps({"Error": err}), status=errcode, mimetype='application/json')
