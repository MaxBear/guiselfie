from flask import request, jsonify, Response, Blueprint
from flask_security import login_required
from flask_login import current_user
import logging, json
from selfie import mysql
from .util_users import get_user_company_id
from .util_views import view_wrapper
from .utils import execute_query

mod_alerts = Blueprint('alerts', __name__, url_prefix='/alerts', template_folder="templates")

@mod_alerts.route('/api/selfie/addrs', methods=['GET'])
def get_selfie_addrs():
    logger = logging.getLogger('selfie.main')

    db = mysql.connect()

    company_id = get_user_company_id(db)
    logger.info("Company id for \"%s\" is %d" % (current_user.id, company_id))
    if company_id==0:
        return Response(json.dumps({"Error": "Unable to find user company id"}), status=400, mimetype='application/json')
    addrs = ["any"]
    sql = "select distinct SipAddr from Selfie_Hosts where company_id=%d order by SipAddr" % company_id
    cursor = db.cursor()
    cursor.execute(sql)
    entries = cursor.fetchall()
    for e in entries:
        addrs.append(e[0])
    return jsonify(result=addrs)

@mod_alerts.route('/api/alerts', methods=['GET'])
@view_wrapper(IsView=False)
def get_alerts():
    logger = logging.getLogger('selfie.main')
    db = mysql.connect()

    company_id = get_user_company_id(db)
    logger.info("Company id for \"%s\" is %d" % (current_user.id, company_id))
    if company_id==0:
        return Response(json.dumps({"Error": "Unable to find user company id"}), status=400, mimetype='application/json')

    alerts = []
    sql = 'select alert_id, company_id, user_id, src_addr, dst_addr,'
    sql += ' video_rx_lost, video_tx_lost, audio_rx_lost, audio_tx_lost,'
    sql += ' content_rx_lost, dst_email'
    sql += ' from alerts where company_id=%d and user_id=%d' % (company_id, current_user.id)
    cursor = db.cursor()
    cursor.execute(sql)
    entries = cursor.fetchall()
    for e in entries:
        alerts.append({
            'alert_id': e[0],
            'company_id': e[1],
            'user_id': e[2],
            'src_addr': e[3],
            'dst_addr': e[4],
            'video_rx_lost': e[5],
            'video_tx_lost': e[6],
            'audio_rx_lost': e[7],
            'audio_tx_lost': e[8],
            'content_rx_lost': e[9],
            'dst_email': e[10]
            }) 
    return jsonify(result=alerts)

@mod_alerts.route('/api/alert', methods=['POST'])
@view_wrapper(IsView=False)
def add_alert():
    logger = logging.getLogger('selfie.main')

    src_addr  = request.form.get('src_addr', type=str)
    dst_addr  = request.form.get('dst_addr', type=str)
    video_tx_lost  = request.form.get('video_tx_lost', type=float)
    video_rx_lost  = request.form.get('video_rx_lost', type=float)
    audio_tx_lost  = request.form.get('audio_tx_lost', type=float)
    audio_rx_lost  = request.form.get('audio_rx_lost', type=float)
    content_rx_lost  = request.form.get('content_rx_lost', type=float)
    dst_email  = request.form.get('dst_email', type=str)

    if src_addr==None or  len(src_addr.strip())==0: 
        return Response(json.dumps({"Error": "Pleaes enter a valid source adddress"}), status=400, mimetype='application/json')

    if dst_email==None or  len(dst_email.strip())==0: 
        return Response(json.dumps({"Error": "Pleaes enter a valid notification email address"}), status=400, mimetype='application/json')

    db = mysql.connect()
    company_id = get_user_company_id(db)
    sql = "insert into alerts (company_id, user_id, src_addr, dst_addr, video_tx_lost,"
    sql += " video_rx_lost, audio_tx_lost, audio_rx_lost, content_rx_lost, dst_email)"
    sql += " values (%d, %d, \"%s\", \"%s\", %f, %f, %f, %f, %f, \"%s\")" %\
            (company_id, current_user.id, src_addr, dst_addr, video_tx_lost,
            video_rx_lost, audio_tx_lost, audio_rx_lost, content_rx_lost, dst_email)
    try:
        db.cursor().execute(sql)
        db.commit()
        return jsonify(result="New alert is successfully added")
    except Exception as e:
        return Response(json.dumps({"Error": str(e)}), status=500, mimetype='application/json')

@mod_alerts.route('/api/alert/<alertid>', methods=['PATCH'])
@view_wrapper(IsView=False)
def modify_alert(alertid):
    logger = logging.getLogger('selfie.main')
    alert_id = 0
    try:
        alert_id = int(alertid)
    except Exception as e:
        return Response(json.dumps({"Error": 'Please provide a valid alert id'}), status=400, mimetype='application/json')
    db = mysql.connect()
    sql = "update alerts set" 
    ssql = ""
    for f in (request.form.keys()):
        if f in ['src_addr', 'dst_addr', 'dst_email']:
            val = request.form.get(f).strip()
            if len(val)==0:
                return Response(json.dumps({"Error": "Please enter valid value for %s" % f}), status=400, mimetype='application/json')
            if ssql!="":
                ssql += ","
            ssql += "%s=\"%s\"" % (f, val)
        if f in ['video_rx_lost', 'video_tx_lost',
                'audio_rx_lost', 'audio_tx_lost',
                'content_rx_lost']:
            val = request.form.get(f, type=float)
            if val==None:
                return Response(json.dumps({"Error": "Please enter valid value for %s" % f}), status=400, mimetype='application/json')
            if ssql!="":
                ssql += ","
            ssql += "%s=%0f" % (f, val)
    if len(ssql)==0:
        return Response(json.dumps({"Error": "Please provide a valid alert fiedl"}), status=400, mimetype='application/json')
    sql = "update alerts set %s where alert_id=%d" % (ssql, alert_id)
    logger.debug(sql)
    err = execute_query(db, sql)
    if err!=None:
        return Response(json.dumps({"Error": err}), status=500, mimetype='application/json')
    else:
        return jsonify(result="Alert %s is successfully modified." % alertid)

@mod_alerts.route('/api/alert/<alertid>', methods=['DELETE'])
@view_wrapper(IsView=False)
def delete_alert(alertid):
    alert_id = 0
    try:
        alert_id = int(alertid)
    except Exception as e:
        return Response(json.dumps({"Error": 'Please provide a valid alert id'}), status=400, mimetype='application/json')
    db = mysql.connect()
    sql = "delete from alerts where alert_id=%d" % alert_id 
    err = execute_query(db, sql)
    if err!=None:
        return Response(json.dumps({"Error": err}), status=500, mimetype='application/json')
    else:
        return jsonify(result="Alert %s is successfully deleted." % alertid)
