'''
Google credentials class definition
'''

class GoogleCredentials:
    '''
    Packages credentials information for a particular google cloud project
    '''
    # pylint: disable=R0913
    def __init__(self, gcid, project_id, client_id, client_secret, topic, has_space):
        self.gcid = gcid
        self.project_id = project_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.topic = topic
        self.has_space = has_space
