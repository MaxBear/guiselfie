from flask_login import current_user
import re, logging
from selfie import mysql 

def get_user_company_id(db):
    logger = logging.getLogger('selfie.main')
    company_id = 0
    cursor = db.cursor()
    sql = "select company_id from user where id=%d" % current_user.id
    cursor.execute(sql)
    entries = cursor.fetchall()
    for e in entries:
        company_id = e[0]
    logger.debug("The company_id for \"%s\" is %d" % (current_user.email, company_id))
    return company_id

def is_user_admin():
    logger = logging.getLogger('selfie.main')
    res = False
    sql = "select admin from user where id=%d" % current_user.id
    db = mysql.connect()
    cursor = db.cursor()
    cursor.execute(sql)
    entries = cursor.fetchall()
    for e in entries:
        res = e[0]==1
    logger.debug("User \"%s\" is admin %s" % (current_user.email, res))
    return res

def password_errors(password): 
    logger = logging.getLogger('selfie.main')
    length_error = len(password) > 64 or len(password) < 8
    alpha_error = re.search(r"[A-Za-z]", password) is None
    digit_error = re.search(r"\d", password) is None
    if length_error:
        logging.debug("Pass length error %d" % len(password))
    if  alpha_error:
        logging.debug("Alpha error")
    if digit_error:
        logging.debug("Digit error")
    return length_error or alpha_error or digit_error
