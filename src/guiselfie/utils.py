def execute_query(db, sql):
    error = None
    try:
        db.cursor().execute(sql)
        db.commit()
    except Exception as e:
        error = str(e)
    return error
