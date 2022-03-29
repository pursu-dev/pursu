'''
Responsible for generating hard-coded company suggestions (Insight 3)
'''

from collections import defaultdict
import pandas as pd

MAX_MATCHES = 20 # Hard-coded limit of matches

mappings = {
    '1-10': 0,
    '11-50': 0,
    '51-200': 0,
    '201-500': 1,
    "501-1K": 1,
    '1K-5K': 2,
    '5K-10K': 3,
    '10K+': 4
}


def size_to_bucket(string):
    '''
    Convert size to encoded bucket
    '''
    if pd.isnull(string):
        return -1
    return mappings[string]


def generateSuggestions(cid, appConfig):
    '''
    Generate company suggestions for a single company
    '''
    query = "SELECT size_category, sector FROM companies WHERE cid={};".format(cid)
    (size_category, sector) = appConfig.DB_CONN.execute_select_query(query)[0]

    sim_size_query = "SELECT cid FROM companies WHERE size_category={} AND user_created=0;".format(
        size_category)
    db_res = appConfig.DB_CONN.execute_select_query(sim_size_query)
    size_matches = [res[0] for res in list(db_res)]

    sim_sector_query = "SELECT cid FROM companies WHERE sector='{}' AND user_created=0;".format(
        sector)
    db_res = appConfig.DB_CONN.execute_select_query(sim_sector_query)
    sector_matches = [res[0] for res in list(db_res)]


    # Grab all companies which match size bucket or sector
    seen = set()
    res = defaultdict(int)
    num_matches = 0
    if size_category in (5, 6):
        for company in size_matches:
            if num_matches < MAX_MATCHES:
                if company not in seen and company != cid:
                    seen.add(company)
                    num_matches += 1
                    res[company] = 1
            else:
                break

    for company in sector_matches:
        if num_matches < MAX_MATCHES:
            if company not in seen and company != cid:
                seen.add(company)
                num_matches += 1
                res[company] = 2
        else:
            break

    for company in size_matches:
        if num_matches < MAX_MATCHES:
            if company not in seen and company != cid:
                seen.add(company)
                num_matches += 1
                res[company] = 3
        else:
            break

    return res


def addToDB(df, appConfig):
    '''
    Add generated suggestions to database
    '''
    values_string = ''
    for _index, row in df.iterrows():
        values_string += '('
        values_string += str(row['cid']) + ',' + str(row['similar']) + ',' + str(row['order'])
        values_string += '), '

    values_string = values_string[:-2]
    values_string += ';'

    query = "INSERT INTO company_suggestions (cid1, cid2, ord) VALUES {}".format(values_string)
    appConfig.DB_CONN.execute_insert_query(query)


def compileSuggestions(suggestion, cid):
    '''
    Compile company suggestions into one dataframe
    '''
    df = pd.DataFrame(columns=['cid1', 'cid2', 'ord'])
    company_list = [cid for i in range(len(suggestion))]
    df['cid1'] = pd.Series((v for v in company_list))
    df['cid2'] = pd.Series((v for v in suggestion.keys()))
    df['ord'] = pd.Series((suggestion[v] for v in suggestion.keys()))
    return df


def generate_insights(appConfig):
    '''
    Generate company suggestions and populate database
    '''
    suggestions = pd.DataFrame(columns=['cid1', 'cid2', 'ord'])
    query = "SELECT name, cid FROM companies WHERE user_created=0;"
    db_res = appConfig.DB_CONN.execute_select_query(query)

    for res in db_res:
        company = res[0]
        cid = res[1]
        suggestion = generateSuggestions(cid, appConfig)
        suggestions = suggestions.append(compileSuggestions(suggestion, cid))
        print("Generated for {}".format(company))

    out_df = suggestions[(suggestions['cid1'] != -1) & (suggestions['cid2'] != -1)]
    addToDB(out_df, appConfig)
