'''
Responsible for generating trending companies (highest relative activity)
based on a specific time duration
'''

def delete_previous_trending_companies(appConfig):
    '''
    Generate trending companies based on a specific timeframe
    '''
    query = "DELETE FROM trending_companies;"
    appConfig.DB_CONN.execute_delete_query(query)

def generate_trending_companies(appConfig):
    '''
    Generate trending companies based on a specific timeframe
    '''
    query = "SELECT P.cid, (Count(*) * 1.0 / GREATEST((SELECT COUNT(*) FROM pipelines\
             WHERE cid=p.cid AND timestamp < date_trunc('day', Now()  - interval '1 WEEK')\
             AND timestamp >= date_trunc('day', Now() - interval '2 WEEK') AND stage!=6), 1))\
             FROM pipelines p WHERE timestamp >= date_trunc('day', Now() - interval '1 WEEK')\
             AND stage!=6 GROUP BY cid HAVING\
             (select count(*) from pipelines where cid=p.cid) > 5;"
    query_result = appConfig.DB_CONN.execute_select_query(query)
    query_result = [q for q in query_result if q[1] > 1.0]
    return query_result

def add_trending_companies_to_db(query_result, appConfig):
    '''
    Add generated trending companies to database
    '''
    values_string = ''
    for [cid, _] in query_result:
        values_string += '('
        values_string += str(cid)
        values_string += '), '

    values_string = values_string[:-2]
    values_string += ';'

    if len(query_result) > 0:
        query = "INSERT INTO trending_companies (cid) VALUES {}".format(values_string)
        appConfig.DB_CONN.execute_insert_query(query)

def generate_trends(appConfig):
    '''
    Generate trending companies and populate database
    '''
    delete_previous_trending_companies(appConfig)
    trending = generate_trending_companies(appConfig)
    add_trending_companies_to_db(trending, appConfig)
