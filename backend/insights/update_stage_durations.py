'''
Module for filling stage_durations table with time spent in each stage (Insight 1)
'''

#pylint: disable=too-many-arguments
from collections import defaultdict

MIN_THRESHOLD = 2
OFFER_STAGE = 5

def select_or_update_duration(appConfig, cid, stage, duration, num_stages):
    '''
    Function that inserts or updates duration in db
    '''
    query = "SELECT duration, num_stages FROM stage_durations \
                WHERE cid={} AND stage={};".format(cid, stage)
    existing_res = appConfig.DB_CONN.execute_select_query(query)

    if existing_res == []:
        insert_query = "INSERT INTO stage_durations (cid, stage, duration, num_stages) \
            VALUES ({}, {}, {}, {});".format(cid, stage, duration, num_stages)
        appConfig.DB_CONN.execute_insert_query(insert_query)
    else:
        current_stage_durations = existing_res[0]
        prev_duration = current_stage_durations[0]
        prev_num_stages = current_stage_durations[1]
        total_stages = num_stages + prev_num_stages
        weighted_sum = (prev_duration * prev_num_stages) + (duration * num_stages)
        new_duration = weighted_sum / total_stages
        update_query = "UPDATE stage_durations SET duration={}, num_stages={} WHERE cid={} \
             AND stage={};".format(new_duration, total_stages, cid, stage)
        appConfig.DB_CONN.execute_update_query(update_query)

def update_timestamps(appConfig, cid, stage, min_timestamp, max_timestamp):
    '''
    Function that inserts or updates duration in db
    '''
    update_query = "INSERT INTO stage_durations(cid, stage, min_date, max_date) \
            VALUES({cid}, {stage}, '{min_date}', '{max_date}') \
            ON CONFLICT (cid, stage) \
            DO UPDATE SET min_date=('{min_date}'), \
            max_date=('{max_date}');".format(cid=cid, stage=stage,
                                             min_date=min_timestamp,
                                             max_date=max_timestamp)
    appConfig.DB_CONN.execute_update_query(update_query)


def get_pipeline_start_duration(full_pipeline):
    '''
    Function to calculate duration for stage that starts pipeline
    (picks between starting at app_conf or referral)
    '''
    app_pipeline_valid, referral_pipeline_valid = False, False
    if 0 in full_pipeline.keys():
        app_conf_count = full_pipeline[0][0]
        app_conf_duration = full_pipeline[0][1]
        app_pipeline_valid = app_conf_count >= MIN_THRESHOLD

    if 1 in full_pipeline.keys():
        referral_count = full_pipeline[1][0]
        referral_duration = full_pipeline[1][1]
        referral_pipeline_valid = referral_count >= MIN_THRESHOLD

    total_duration = 0
    if app_pipeline_valid and referral_pipeline_valid:
        total_duration = (app_conf_duration + referral_duration) / 2
    elif app_pipeline_valid:
        total_duration = app_conf_duration
    elif referral_pipeline_valid:
        total_duration = referral_duration
    else:
        total_duration = -1

    return total_duration


def update_full_pipeline_duration(appConfig, full_pipeline, cid):
    '''
    Function to update start-end pipeline duration
    '''
    total_duration = get_pipeline_start_duration(full_pipeline)

    if total_duration < 0 or 3 not in full_pipeline.keys():
        return

    total_count = 0

    for stage, value in full_pipeline.items():
        count, duration = value[0], value[1]
        total_count = max(count, total_count)
        if stage not in [0, 1]:
            if count <= MIN_THRESHOLD:
                return
            total_duration += duration

    select_or_update_duration(appConfig, cid, -1, total_duration, total_count)


def update_stage_durations(appConfig):
    '''
    Function that fetches the companies that had updates in the last 30 days
    '''
    query = "SELECT cid FROM stages WHERE timestamp > NOW() - INTERVAL '7 days' GROUP BY cid;"
    res = appConfig.DB_CONN.execute_select_query(query)
    for cid in res:
        cid = cid[0]
        query = "SELECT COUNT(*), stage, AVG(duration) FROM stages WHERE \
            duration IS NOT NULL AND timestamp > NOW() - INTERVAL '7 days' \
            AND cid={} GROUP BY stage;".format(cid)
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

def insert_timestamp_data(appConfig, stage, cid):
    '''
    Completes all the computation related to timestamps and updates the db
    '''
    timestamp_query = "SELECT timestamp FROM stages WHERE \
                    cid={} AND stage={};".format(cid, stage)
    timestamp_data = appConfig.DB_CONN.execute_select_query(timestamp_query)
    flattened_data = [item for sublist in timestamp_data for item in sublist]
    timestamp_parsed = [x.strftime("%m-%d") for x in flattened_data]
    sorted_timestamp_parsed = sorted(timestamp_parsed)
    min_date_timestamp, max_date_timestamp = find_max_min_dates(sorted_timestamp_parsed)
    if (min_date_timestamp, max_date_timestamp) == (None, None):
        return
    update_timestamps(appConfig, cid, stage, min_date_timestamp, max_date_timestamp)

def find_max_min_dates(timestamps_parsed):
    '''
    Function that finds the min and max dates relative to 06-01 in a sorted list
    '''
    if timestamps_parsed == []:
        return None, None
    value = "06-01"
    low = 0
    high = len(timestamps_parsed) - 1
    if timestamps_parsed[low] >= value:
        return timestamps_parsed[low], timestamps_parsed[high]
    if timestamps_parsed[high] <= value:
        return timestamps_parsed[low], timestamps_parsed[high]
    while low <= high:
        mid = int((high + low) / 2)
        if value < timestamps_parsed[mid]:
            high = mid - 1
        elif value > timestamps_parsed[mid]:
            low = mid + 1
        else:
            return timestamps_parsed[mid+1], timestamps_parsed[mid-1]
    return timestamps_parsed[low], timestamps_parsed[high]
