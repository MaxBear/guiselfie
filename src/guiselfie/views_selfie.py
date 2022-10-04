from flask import request, redirect, render_template, jsonify, Response, make_response, Blueprint
from flask_login import current_user
from flask_security import login_required
from datetime import datetime, timedelta
import json, logging 
from selfie import mysql
from .util_views import view_wrapper
from .util_users import get_user_company_id, is_user_admin

mod_selfie = Blueprint('selfie', __name__, url_prefix='/selfie', template_folder="templates")

def get_uris(db):
    logger = logging.getLogger('selfie.main')
    cursor = db.cursor()
    result = []

    company_id = get_user_company_id(db)
    if company_id==0:
        return result

    sql = 'select distinct SipAddr from Selfie_Hosts where company_id=%d' % company_id
    cursor.execute(sql)
    entries = cursor.fetchall()
    for e in entries:
        result.append(e[0]) 
    logger.debug("The destination sip url for \"%s\" is %s" % (current_user.email, ','.join(map(str, result))))
    return result

def get_dst_tags(db):
    logger = logging.getLogger('selfie.main')
    cursor = db.cursor()
    result = []

    company_id = get_user_company_id(db)
    if company_id==0:
        return result

    sql = 'select distinct Tag from Selfie_Hosts where company_id=%d' % company_id
    cursor.execute(sql)
    entries = cursor.fetchall()
    for e in entries:
        result.append(e[0]) 
    logger.debug("The destination tags for \"%s\" are %s" % (current_user.email, ','.join(map(str, result))))
    return result

def get_usage_d3js(db, dt_start, dt_end, search_key):
    is_admin = is_user_admin()
    dst_tags_filter = get_dst_tags(db)
    if not is_admin and len(dst_tags_filter)==0:
        return [[], {}]
    dst_tags = {}
    d3data = []
    cursor = db.cursor()
    sql = "select distinct s.Id, s.StartUtc, s.DstTag from Sessions as s join Session_Medias as m on s.Id=m.SessionId"
    sql += " where s.StartUtc>=\"%s\" and s.StartUtc<=\"%s\"" % (dt_start, dt_end)
    if not is_admin:
        sql += " and not s.SrcUri like \"%%mns.vc%%\""
    if not is_admin and len(dst_tags_filter)>0:
        sql += " and s.DstTag in (%s)" % ','.join("\"" + str(u) + "\"" for u in dst_tags_filter)
    if (search_key!="" and search_key!="*"): 
        sql += " and CONCAT_WS('_', StartUtc, SrcUri, DstUri, DstTag) like \"%%%s%%\"" % search_key      
    sql += " order by s.StartUtc desc"
    cursor.execute(sql)
    rows = cursor.fetchall()
    for row in rows:
        dst_tag = row[2].strip()
        if len(dst_tag)==0:
            dst_tag = "null"
        d3data.append({
            'time': row[1],\
            'dst_tag': dst_tag
        })
        if dst_tag not in dst_tags:
            dst_tags[dst_tag] = 0
        dst_tags[dst_tag] += 1 
    d3data.sort(key=lambda item:item['time'])
    dst_tags_sorted = {k: v for k, v in sorted(dst_tags.items(), key=lambda item: item[1], reverse=True)}
    return [list(dst_tags_sorted.keys()), d3data]

def get_usage(db, dt_start, dt_end, page_size, page_idx, search_key, gen_csv=False):
    logger = logging.getLogger('selfie.main')
    is_admin = is_user_admin()
    dst_tags_filter = get_dst_tags(db)
    if not is_admin and len(dst_tags_filter)==0:
        return {'TotalEntries': 0, 'Entries': [], 'Csv': ""}
    csv = "id, time, server, duration, TxBw, RxBw, established, status, src_uri, dst_uri, dst_tag,"
    csv += "video_raddr, video_rport, video_TxPkt, video_TxLost, video_TxJitter, video_RxPkt, video_RxLost, video_RxJitter,"
    csv += "audio_raddr, audio_rport, audio_TxPkt, audio_TxLost, audio_TxJitter, audio_RxPkt, audio_RxLost, audio_RxJitter,"
    csv += "content_raddr, content_rport, content_TxPkt, content_TxLost, content_TxJitter, content_RxPkt, content_RxLost, content_RxJitter\n"
    allids = []
    fulldata = []
    cursor = db.cursor()
    sql = "select Id from Sessions as s join Session_Medias as m on s.Id=m.SessionId"
    sql += " where StartUtc>=\"%s\" and StartUtc<=\"%s\"" % (dt_start, dt_end)
    if not is_admin:
        sql += " and not s.SrcUri like \"%%mns.vc%%\""
    if not is_admin and len(dst_tags_filter)>0:
        sql += " and s.DstTag in (%s)" % ','.join("\"" + str(u) + "\"" for u in dst_tags_filter)
    if (search_key!="" and search_key!="*"): 
        sql += " and CONCAT_WS('_', StartUtc, SrcUri, DstUri, DstTag) like \"%%%s%%\"" % search_key      
    sql += " order by StartUtc desc"
    logger.debug("get_usage sql: \"%s\"", sql)
    cursor.execute(sql)
    rows = cursor.fetchall()
    for row in rows:
        sid = row[0]
        if not sid in allids:
            allids.append(sid)

    if len(allids)==0:
        return {'TotalEntries': len(allids), 'Entries': fulldata, 'Csv': csv}

    if page_size>=0:
        i = page_idx * page_size
        f = (page_idx + 1) * page_size 
        ids = allids[i:f] 
    else:
        ids = allids
    t = ','.join("\"" + str(i) + "\"" for i in ids)
    logger.debug("get_usage t: \"%s\"", t)

    result = {}
    sql = "select s.Id, s.StartUtc, r.Hostname, s.Duration, s.TxBw, s.RxBw, s.Established, s.Status,"
    sql += " s.SrcUri, s.DstUri, m.Raddr, m.Rport, m.Type, m.TxPkt, m.TxLost, m.TxJItter, m.RxPkt, m.RxLost, m.RxJItter, s.DstTag"
    sql += " from Sessions as s left join Rend_Servers as r on s.RendServer=r.IpAddr"
    sql += " join Session_Medias as m on s.Id=m.SessionId"
    sql += " where s.Id in (%s)" % t
    sql += " order by s.StartUtc"
    logger.debug("get_usage: sql: \"%s\"", sql)
    cursor.execute(sql)
    rows = cursor.fetchall()
    for row in rows:
        sid = row[0]
        stream_type = row[12]
        TkPkt = row[13]
        TxLost = row[14]
        TxJitter = row[15]
        if stream_type.lower()=="video" and TkPkt==0 and TxLost==0 and TxJitter==0: 
            stream_type = "content"
        stream_stats = {
            'raddr': row[10],\
            'rport': row[11],\
            'type': row[12],\
            'TxPkt': TkPkt,\
            'TxLost': TxLost,\
            'TxJitter': TxJitter,\
            'RxPkt': row[16],\
            'RxLost': row[17],\
            'RxJitter': row[18]}
        if not sid in result:
            dst_tag = row[19]
            if len(dst_tag.strip())==0:
                dst_tag = "null"
            result[sid] = {
                'start_time': row[1].strftime("%Y-%m-%d %H:%M:%S"),\
                'address': row[2],\
                'duration': row[3],\
                'TxBw': row[4],\
                'RxBw': row[5],\
                'Established': "yes" if row[6]==1 else "no",\
                'Status': row[7],\
                'src_uri': row[8],\
                'dst_uri': row[9],\
                'dst_tag': dst_tag,\
                stream_type: stream_stats}
        else:
            result[sid][stream_type] =  stream_stats

    for k, v in result.items() :
        fulldata.append({
            'id': k,\
            'time': v['start_time'],\
            'address': v['address'],\
            'duration': v['duration'],\
            'TxBw': v['TxBw'],\
            'RxBw': v['RxBw'],\
            'established': v['Established'],\
            'status': v['Status'],\
            'src_uri': v['src_uri'],\
            'dst_uri': v['dst_uri'],\
            'dst_tag': v['dst_tag'],\
            'video_raddr': v['video']['raddr'] if 'video' in v.keys() else "",\
            'video_rport': v['video']['rport'] if 'video' in v.keys() else  0,\
            'video_TxPkt': v['video']['TxPkt'] if 'video' in v.keys() else 0 ,\
            'video_TxLost': v['video']['TxLost'] if 'video' in v.keys() else 0,\
            'video_TxJitter': v['video']['TxJitter'] if 'video' in v.keys() else 0,\
            'video_RxPkt': v['video']['RxPkt'] if 'video' in v.keys() else 0,\
            'video_RxLost': v['video']['RxLost'] if 'video' in v.keys() else 0,\
            'video_RxJitter': v['video']['RxJitter'] if 'video' in v.keys() else 0,\
            'audio_raddr': v['audio']['raddr'] if 'audio' in v.keys() else"",\
            'audio_rport': v['audio']['rport'] if 'audio' in v.keys() else 0,\
            'audio_TxPkt': v['audio']['TxPkt'] if 'audio' in v.keys() else 0,\
            'audio_TxLost': v['audio']['TxLost'] if 'audio' in v.keys() else 0,\
            'audio_TxJitter': v['audio']['TxJitter'] if 'audio' in v.keys() else  0,\
            'audio_RxPkt': v['audio']['RxPkt'] if 'audio' in v.keys() else 0,\
            'audio_RxLost': v['audio']['RxLost'] if 'audio' in v.keys() else 0,\
            'audio_RxJitter': v['audio']['RxJitter'] if 'audio' in v.keys() else  0,\
            'content_raddr': v['content']['raddr'] if 'content' in v.keys() else "",\
            'content_rport': v['content']['rport'] if 'content' in v.keys() else  0,\
            'content_TxPkt': v['content']['TxPkt'] if 'content' in v.keys() else 0,\
            'content_TxLost': v['content']['TxLost'] if 'content' in v.keys() else 0,\
            'content_TxJitter': v['content']['TxJitter'] if 'content' in v.keys() else 0,\
            'content_RxPkt': v['content']['RxPkt'] if 'content' in v.keys() else 0,\
            'content_RxLost': v['content']['RxLost'] if 'content' in v.keys() else 0,\
            'content_RxJitter': v['content']['RxJitter'] if 'content' in v.keys() else 0,\
        })

    fulldata.sort(key=lambda item:item['time'], reverse=True)

    if gen_csv:
        for v in fulldata:
            csv += "%s, %s, %s, %d,\
                        %d, %d, %s, %s, %s, %s, %s,\
                        %s, %d, %d, %d, %d, %d, %d, %d,\
                        %s, %d, %d, %d, %d, %d, %d, %d,\
                        %s, %d, %d, %d, %d, %d, %d, %d\n" %\
                        (v['id'], v['time'], v['address'], v['duration'],\
	                v['TxBw'], v['RxBw'], v['established'], v['status'], v['src_uri'], v['dst_uri'], v['dst_tag'],\
	                v['video_raddr'], v['video_rport'], v['video_TxPkt'], v['video_TxLost'], v['video_TxJitter'], v['video_RxPkt'], v['video_RxLost'], v['video_RxJitter'],\
	                v['audio_raddr'], v['audio_rport'], v['audio_TxPkt'], v['audio_TxLost'], v['audio_TxJitter'], v['audio_RxPkt'], v['audio_RxLost'], v['audio_RxJitter'],\
	                v['content_raddr'], v['content_rport'], v['content_TxPkt'], v['content_TxLost'], v['content_TxJitter'], v['content_RxPkt'], v['content_RxLost'], v['content_RxJitter'])
    else: 
        csv = ""
    return {'TotalEntries': len(allids), 'Entries': fulldata, 'Csv': csv}

@mod_selfie.route('/stats', methods=['GET'])
@view_wrapper(IsView=True, AdminRequired=False)
def stats():
    db = mysql.connect()
    dst_uris = get_uris(db)
    return render_template('selfie/index.html', dst_uris=json.dumps(dst_uris))

def get_time_range(frm):
    err = startt = endt = None
    start_time = frm.get('start_time')
    end_time = frm.get('end_time')

    if not start_time:
        return [None, None, "Please specify a valid start_time in form data"]

    if not end_time :
        return [None, None, "Please specify a valid end_time in form data"]

    try:
        startt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return [None, None, "Please specify a valid start_time in form data"]

    try:
        endt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return [None, None, "Please specify a valid end_time in form data"]

    return [startt, endt, err]

def get_page_props(frm):
    err = page_size = page_idx = None
    page_size = frm.get('page_size')
    page_idx = frm.get('page_idx')

    if not page_size:
        return [None, None, "Please specify a valid page_size in form data"]

    if not page_idx:
        return [None, None, "Please specify a valid page_idx in form data"]

    try:
        psize = int(page_size)
    except ValueError:
        if page_size=='all':
            psize = -1
        else:
            return [None, None, "Please specify a valid page_size in form data"]

    try:
        pidx = int(page_idx)
    except ValueError:
        return [None, None, "Please specify a valid page_idx in form data"]

    return [psize, pidx, err]

def get_search_key(frm):
    search_key = frm.get('search_key')
    
    if search_key:
        search_key = search_key.strip()
    else:
        search_key = ""

    return search_key


@mod_selfie.route('/api/usage', methods=['POST'])
@view_wrapper(IsView=False)
def usage():
    [startt, endt, err] = get_time_range(request.form)
    if err:
        return Response(json.dumps({"Error": err}), status=400, mimetype='application/json')
    
    [page_size, page_idx, err ] = get_page_props(request.form)
    if err:
        return Response(json.dumps({"Error": err}), status=400, mimetype='application/json')

    search_key = get_search_key(request.form)

    db = mysql.connect()

    return jsonify(get_usage(db, startt, endt, page_size, page_idx, search_key))

@mod_selfie.route('/api/usage/d3js', methods=['POST'])
@view_wrapper(IsView=False)
def usage_d3js():
    [startt, endt, err] = get_time_range(request.form)
    if err:
        return Response(json.dumps({"Error": err}), status=400, mimetype='application/json')

    search_key = get_search_key(request.form)

    db = mysql.connect()
    dst_tags, d3data = get_usage_d3js(db, startt, endt, search_key)

    return jsonify(dst_tags=dst_tags, d3data=d3data)

@mod_selfie.route('/api/usage/csv', methods=['POST'])
@view_wrapper(IsView=False)
def usage_csv():
    [startt, endt, err] = get_time_range(request.form)
    if err:
        return Response(json.dumps({"Error": err}), status=400, mimetype='application/json')

    search_key = get_search_key(request.form)
   
    csv = ""
    db = mysql.connect()
    dst_uris = get_uris(db)
    if len(dst_uris) > 0:
        result = get_usage(db, startt, endt, -1, 0, search_key, True)
        csv = result['Csv']

    response = make_response(csv)
    response.headers["Content-Disposition"] = "attachment; filename=selfis.csv"
    return response
