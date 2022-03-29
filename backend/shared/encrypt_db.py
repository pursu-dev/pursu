'''Script to encrypt raw user token from database'''
from psycopg2 import sql

from shared import config

def encrypt_db(appConfig):
    '''
    Function to Encrypt the Database's Refresh Tokens using a predefined Encryption Key
    '''
    query = sql.SQL("SELECT uid FROM gmail;")
    res = appConfig.DB_CONN.execute_select_query(query)
    res = [r[0] for r in res]
    for uid in res:
        select_query = sql.SQL("SELECT token FROM gmail WHERE uid={};").format(sql.Literal(uid))
        token = appConfig.DB_CONN.execute_select_query(select_query)[0][0]
        token = token.encode('utf-8')
        encrypted_token = appConfig.TOKEN_CIPHER_SUITE.encrypt(token)
        encrypted_token = encrypted_token.decode('utf-8')
        update_query = sql.SQL("UPDATE gmail SET token={} WHERE uid={};").format(
            sql.Literal(encrypted_token), sql.Literal(uid))
        appConfig.DB_CONN.execute_update_query(update_query)

def decrypt_db(appConfig):
    '''
    Function to Decrypt the Database's Refresh Tokens using a predefined Encryption Key
    '''
    query = sql.SQL("SELECT uid FROM gmail;")
    res = appConfig.DB_CONN.execute_select_query(query)
    res = [r[0] for r in res]
    for uid in res:
        select_query = sql.SQL("SELECT token FROM gmail WHERE uid={};").format(sql.Literal(uid))
        token = appConfig.DB_CONN.execute_select_query(select_query)[0][0]
        token = token.encode('utf-8')
        decrypted_token = appConfig.TOKEN_CIPHER_SUITE.decrypt(token)
        decrypted_token = decrypted_token.decode('utf-8')
        update_query = sql.SQL("UPDATE gmail SET token={} WHERE uid={};") \
                          .format(sql.Literal(decrypted_token), sql.Literal(uid))
        appConfig.DB_CONN.execute_update_query(update_query)

if __name__ == "__main__":
    encrypt_db(config.ProductionConfig())
