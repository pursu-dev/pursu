'''
Module for scraping email.
'''
import re
import base64
import datetime

from bs4 import BeautifulSoup
import dateparser
import pytz

def get_url(page):
    '''Function to get url.'''
    start_link = page.find('https://')
    if start_link == -1:
        return None, 0
    potential_end_links = ['/>', '<', '"']
    end_candidates = [page.find(pend, start_link + 1) for pend in potential_end_links]
    end_link = min([end for end in end_candidates if end >= 0])
    url = page[start_link : end_link]
    return url, end_link


def get_links(page):
    '''Function to get links.'''
    page = str(BeautifulSoup(page, features="html.parser"))
    links = []
    while True:
        url, quote = get_url(page)
        page = page[quote:]

        # Get all URLS that are not email links
        if url:
            if '@' not in url:
                links.append(url)
        else:
            break
    return links


def parse_multitype_parts(multitype_parts):
    '''Function to parse multi-part types.'''
    text = ''
    links = []
    regex = r'(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+'

    for part in multitype_parts:
        #import pdb; pdb.set_trace()
        mime_type = part['mimeType']
        if mime_type.find('multipart/') >= 0:
            multitype_parts.extend(part['parts'])
        elif mime_type == 'text/plain':
            body = base64.urlsafe_b64decode(
                part['body']['data']).decode('utf-8')
            text = body.replace('\n', ' ').replace('\r', '')
            text = text.replace('\n', ' ').replace('\r', '')
            #text = re.sub(regex, '', text)
        elif mime_type == 'text/html':
            #h = html2text.HTML2Text()
            body = base64.urlsafe_b64decode(
                part['body']['data']).decode('utf-8')

            links = get_links(body)
            soup = BeautifulSoup(body, 'lxml')
            body = soup.text
            #body = h.handle(body)
            text = body.replace('\n', ' ').replace('\r', '')
            text = re.sub(regex, '', text)
    return text, links


def scrape_email_info(resp, to_lower=True):
    '''Function to scrape email info.'''
    # Get header information
    msg_id = resp['id']

    receiver = ''
    sender = ''
    reply_to = ''
    date = None
    for header in resp['payload']['headers']:
        if header['name'] == 'Date':
            # datetime object
            my_value = header['value'].replace('(UTC)', '').rstrip()
            date = dateparser.parse(my_value)
        elif header['name'] == 'Subject':
            subj = header['value']
        elif header['name'] == 'From':
            sender = header['value']
        elif header['name'] == 'To':
            receiver = header['value']
        elif header['name'] == 'Reply-To':
            reply_to = header['value']

    # Ensure that we always have a valid timestamp
    # UTC localization ensures that the timestamp is offset-aware
    if date is None:
        date = pytz.utc.localize(datetime.datetime.utcnow())
    text = ''
    links = []
    mime_type = resp['payload']['mimeType']

    regex = r'(?:(?:https?|ftp):\/\/)?[\w/\-?=%.]+\.[\w/\-?=%.]+'

    try:
        # Check if mimeType: text/plain:
        if mime_type.find('multipart/') < 0:
            if mime_type == 'text/plain':
                text = base64.urlsafe_b64decode(
                    resp['payload']['body']['data']).decode('utf-8')
                text = text.replace('\n', ' ').replace('\r', '')
                text = re.sub(regex, '', text)
            elif mime_type == 'text/html':
                #h = html2text.HTML2Text()
                body = base64.urlsafe_b64decode(
                    resp['payload']['body']['data']).decode('utf-8')
                links = get_links(body)
                soup = BeautifulSoup(body, 'lxml')
                body = soup.text
                #text = h.handle(body)
                text = body.replace('\n', ' ').replace('\r', '')
                text = re.sub(regex, '', text)
                text = re.sub(r'http.* ', '', text)
            else:
                print("ERROR: UNABLE TO PARSE because of mimeType {}".format(mime_type))
        else:
            text, links = parse_multitype_parts(resp['payload']['parts'])

        email_info = {}

        text = re.sub(r'/', '-', text)
        text = re.sub(r'[^A-Za-z0-9\- ]+', '', text)
        text = re.sub(r'\t', ' ', text)
        sender = re.sub(r'"', '', sender)

        email_info['id'] = msg_id
        email_info['timestamp'] = date
        email_info['receiver'] = receiver
        email_info['subject'] = subj
        email_info['sender'] = sender
        email_info['body'] = text

        if to_lower:
            email_info['receiver'] = email_info['receiver'].lower()
            email_info['subject'] = email_info['subject'].lower()
            email_info['sender'] = email_info['sender'].lower()
            email_info['body'] = email_info['body'].lower()

        email_info['links'] = links
        email_info['reply_to'] = reply_to
        return email_info
    except Exception as e:
        print('Couldn\'t parse email', e)
        return None
