''' Script to scrape Pitt CSC Repo and add to database '''
# noqa: C0301  pylint: disable=C0301
from collections import defaultdict
import difflib
import requests
from psycopg2 import sql


def get_company_name(name_and_link):
    '''
    Parse company name from row.
    '''
    name_start = name_and_link.find('[')
    closed = (name_start == -1)

    if closed:
        return name_and_link.strip(), closed

    name_end = name_and_link.find(']')
    company_name = name_and_link[name_start + 1: name_end]

    closed = "<del>" in company_name
    return company_name, closed


def get_link(row):
    '''
    Parse link from row.
    '''
    link_start = row.find('](')
    link_end = row[link_start + 2:].find('|')

    return row[link_start + 2: link_end - 1]


def generate_jobs_lists():
    '''
    Dynamic list of available job listing tables and whether they are internships.
    '''
    return [["https://raw.githubusercontent.com/pittcsc/Summer2022-Internships/master/README.md", True],
            ["https://raw.githubusercontent.com/coderQuad/New-Grad-Positions-2022/master/README.md", False]]


class JobListingUpdateManager():
    '''
    Scrapes and updates internships and jobs.
    '''

    def parse_markdown_file(self):
        '''
        Return relevant part of downloaded file.
        '''
        downloaded_file = self.downloaded_file.text
        column_names = ["Name", "Location", "Notes"]
        rows_to_skip = 2
        downloaded_file = downloaded_file.split('\n')

        for line in downloaded_file:
            if not all(x in line for x in column_names):
                rows_to_skip += 1
            else:
                break
        return downloaded_file[rows_to_skip:]

    def insert_into_table(self, company_name, approved, cid, is_internship):
        '''
        Helper function to insert new job posting into database.
        '''
        if cid is None:
            query = sql.SQL("INSERT INTO jobs(name, approved, internship) VALUES \
                ({}, {}, {})").format(sql.Literal(company_name), sql.Literal(approved),
                                      sql.Literal(is_internship))
        else:
            query = sql.SQL("INSERT INTO jobs(name, approved, cid, internship) VALUES \
                ({}, {}, {}, {})").format(sql.Literal(company_name), sql.Literal(approved),
                                          sql.Literal(cid), sql.Literal(is_internship))

        self.appConfig.DB_CONN.execute_insert_query(query)

    def match_companies(self, is_internship):
        '''
        Find company match for job listing.
        '''
        for listing in self.parsed_list:
            company_name, link = listing[0], listing[1]
            query = sql.SQL(
                "SELECT COUNT(*) FROM jobs WHERE name={} AND internship={}").format(
                    sql.Literal(company_name), sql.Literal(is_internship))
            count = self.appConfig.DB_CONN.execute_select_query(query)[0][0]

            if count > 0:  # match found - company already in pitt csc list
                continue

            # select all except user created companies
            query = sql.SQL("SELECT name, domain, cid FROM companies where user_created != 1")
            res = self.appConfig.DB_CONN.execute_select_query(query)

            company_info = defaultdict(str)
            for row in res:
                company_info[row[0]] = [row[1], row[2]]

            if company_name in company_info.keys():
                cid = company_info[company_name][1]
                self.insert_into_table(
                    company_name=company_name,
                    approved=True,
                    cid=cid,
                    is_internship=is_internship)
                continue

            possible_matches = difflib.get_close_matches(company_name, company_info.keys(), 3)
            if possible_matches == []:
                self.insert_into_table(
                    company_name=company_name,
                    approved=False,
                    cid=None,
                    is_internship=is_internship)
                continue

            match_found = False
            for possible_match in possible_matches:
                domain = company_info[possible_match][0]
                if domain is not None and domain in link:
                    cid = company_info[possible_match][1]
                    self.insert_into_table(
                        company_name=company_name,
                        approved=False,
                        cid=cid,
                        is_internship=is_internship)
                    match_found = True
                    break

            if not match_found:
                self.insert_into_table(
                    company_name=company_name,
                    approved=False,
                    cid=None,
                    is_internship=is_internship)

    def parse_list(self):
        '''
        Parse relevant part of downloaded file.
        '''
        parsed_list = []
        for row in self.data:
            row_list = row.split('|')
            if len(row_list) <= 1:
                continue
            if row_list[0] == "":
                # for some reason the Capital One row doesn't start with '|'
                row_list = row_list[1:]

            company_name, closed = get_company_name(row_list[0])

            if closed:
                continue

            link = get_link(row_list[0])
            location = row_list[1].strip()
            notes = row_list[2].strip()

            parsed_list.append([company_name, link, location, notes])
        return parsed_list


    def update_table(self, is_internship):
        '''
        Update job listing in database when there are changes.
        '''
        query = sql.SQL("SELECT name, link, location, notes FROM jobs WHERE internship={}").format(
            sql.Literal(is_internship))
        jobs_table = self.appConfig.DB_CONN.execute_select_query(query)

        jobs_table = {tuple(x) for x in jobs_table}
        parsed_list = {tuple(x) for x in self.parsed_list}

        updated_rows = parsed_list - jobs_table
        for [name, link, location, notes] in updated_rows:
            if link is None:
                delete_query = sql.SQL("DELETE FROM jobs WHERE name={} AND internship={}").format(
                    sql.Literal(name), sql.Literal(is_internship))
                self.appConfig.DB_CONN.execute_delete_query(delete_query)
            else:
                update_query = sql.SQL("UPDATE jobs SET link={}, location={}, notes={} \
                    WHERE name={} AND internship={}").format(sql.Literal(link),
                                                             sql.Literal(location),
                                                             sql.Literal(notes),
                                                             sql.Literal(name),
                                                             sql.Literal(is_internship))
                self.appConfig.DB_CONN.execute_update_query(update_query)

    def update_jobs(self):
        '''
        Main orchestrating function of this cron job.
        '''
        jobs_lists = generate_jobs_lists()
        for [link, is_internship] in jobs_lists:
            self.downloaded_file = requests.get(link)
            self.data = self.parse_markdown_file()
            self.parsed_list = self.parse_list()
            self.match_companies(is_internship)
            self.update_table(is_internship)

    def __init__(self, _appConfig):
        '''
        Initializes appConfig for this cron job.
        '''
        self.appConfig = _appConfig
        self.downloaded_file, self.data, self.parsed_list = None, None, None
