'''Script to encrypt raw user token from database'''
#pylint: disable=C0301
from collections import defaultdict
from insights.update_stage_durations import select_or_update_duration, update_full_pipeline_duration, insert_timestamp_data
from shared import config

OFFER_STAGE = 5

def update_stage_durations(appConfig):
    '''
    Function that fills stage_durations table
    '''
    query = "SELECT cid FROM stages GROUP BY cid;"
    res = appConfig.DB_CONN.execute_select_query(query)

    for cid in res:
        cid = cid[0]
        query = "SELECT COUNT(*), stage, AVG(duration) FROM stages WHERE \
            duration IS NOT NULL AND cid={} GROUP BY stage;".format(cid)
        stages = appConfig.DB_CONN.execute_select_query(query)
        if stages != []:
            full_pipeline = defaultdict(list)
            for stage_data in stages:
                count, stage, duration = stage_data[0], stage_data[1], int(stage_data[2])
                select_or_update_duration(appConfig, cid, stage, duration, count)
                full_pipeline[stage] = [count, duration]
                insert_timestamp_data(appConfig, stage, cid)
            update_full_pipeline_duration(appConfig, full_pipeline, cid)
        # Inserting in timestamp data for offer manually b/c doesn't have duration
        insert_timestamp_data(appConfig, OFFER_STAGE, cid)

if __name__ == "__main__":
    update_stage_durations(config.ProductionConfig())
