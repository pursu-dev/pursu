''' Unit tests for insight extractor '''

import datetime
import pandas as pd
import helper  # pylint: disable=E0401
from insights import pipeline_updates  # pylint: disable=E0401

def test_update_pipelines(mocker, db_conn, appConfig):
    '''
    Sanity test for update pipelines functions 
    '''
    aws_client = mocker.MagicMock()
    mocker.patch('boto3.client', return_value=aws_client)

    df1 = mocker.MagicMock()
    df2 = pd.DataFrame()
    df1.append.return_value = df1
    current_pipelines = mocker.patch('insights.pipeline_updates.get_pipelines', return_value=df1)
    old_pipelines = mocker.patch('insights.pipeline_updates.get_old_pipelines', return_value=df2)
    write_pipelines = mocker.patch('insights.pipeline_updates.write_pipelines_to_s3')

    pipeline_updates.update_pipelines(appConfig)

    current_pipelines.assert_called_once_with(appConfig)
    old_pipelines.assert_called_once_with(aws_client)
    write_pipelines.assert_called_once_with(df1, aws_client)


