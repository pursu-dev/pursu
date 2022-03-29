CREATE TABLE users (
    uid SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    filt_version INTEGER NOT NULL,
    college VARCHAR(100),
    major VARCHAR(100),
    year INTEGER,
    consent INTEGER DEFAULT 0,
    -- 0 = male, 1 = female, 2 = other, 3 = undisclosed 
    gender INTEGER,
    ethnicity VARCHAR(25),
    login TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    -- track whether user is currently being tracked
    -- set to false by cron job, true by api route
    -- 0 = inactive, 1 = active, -1 = manual user
    active INTEGER DEFAULT 1 NOT NULL
);

CREATE TABLE data_providers (
    email VARCHAR(100) PRIMARY KEY
);

-- frontend uses this table to verify if a user has beta access
CREATE TABLE beta_users (
    email VARCHAR(100) PRIMARY KEY
);

CREATE TABLE bugs (
    bug VARCHAR(280) PRIMARY KEY,
    created TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE feedback (
    fbid SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL,
    comment VARCHAR(280) NOT NULL,
    created TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL
);

CREATE TABLE filters (
    fid SERIAL PRIMARY KEY,
    name VARCHAR(64) NOT NULL,
    query TEXT NOT NULL,
    version INTEGER NOT NULL
);

CREATE TABLE companies (
    cid SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    sector VARCHAR(100),
    description VARCHAR(1000),
    domain VARCHAR(100),
    --- Filter versions are only required for tracked companies
    filt_version INTEGER,
    --- 0: tracked, 1: user added, 2: not tracked + non_user
    user_created INTEGER DEFAULT 0 NOT NULL,
    size_category INTEGER DEFAULT -1 NOT NULL,
    logo VARCHAR(200)
);

CREATE TABLE jobs (
    jid SERIAL PRIMARY KEY,
    cid INTEGER,
    approved BOOLEAN NOT NULL,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(100),
    notes VARCHAR(1000),
    link VARCHAR(500),
    internship BOOLEAN,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL, 
    FOREIGN KEY(cid) REFERENCES companies ON DELETE CASCADE
);

CREATE TABLE recruiters (
    rid SERIAL PRIMARY KEY,
    cid INTEGER NOT NULL,
    name VARCHAR(100),
    email VARCHAR(100) NOT NULL UNIQUE,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(cid) REFERENCES companies ON DELETE CASCADE
);

CREATE TABLE pipelines (
    -- if user manually changes company/recruiter, check for existing. if not, prompt to update company/recruiter table then update pipeline table
    pid SERIAL PRIMARY KEY,
    uid INTEGER NOT NULL,
    cid INTEGER NOT NULL,
    stage INTEGER,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    -- how to check if info on recruiter is correct?
    rid INTEGER,
    notes VARCHAR(500),
    deadline TIMESTAMPTZ,
    link VARCHAR(200),
    active INTEGER DEFAULT 1,
    FOREIGN KEY(uid) REFERENCES users ON DELETE CASCADE,
    FOREIGN KEY(cid) REFERENCES companies ON DELETE CASCADE,
    FOREIGN KEY(rid) REFERENCES recruiters ON DELETE CASCADE
);

-- incorporates parsed deadlines as well as user inputted todos
CREATE TABLE todos (
    tid SERIAL PRIMARY KEY,
    uid INTEGER NOT NULL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    company VARCHAR(100),
    deadline TIMESTAMPTZ,
    pid INTEGER,
    -- user will manually write task description
    -- when deadline parsed from email in analysis, we will convert to human readable format and write here
    task VARCHAR(200) NOT NULL,
    FOREIGN KEY(uid) REFERENCES users ON DELETE CASCADE,
    FOREIGN KEY(pid) REFERENCES pipelines ON DELETE CASCADE
);

CREATE TABLE stages (
    sid SERIAL PRIMARY KEY,
    uid INTEGER NOT NULL,
    cid INTEGER NOT NULL,
    stage INTEGER,
    --duration represents the amount of time (days) a user spends in specified stage: only updated after they progress to the next stage
    duration INTEGER,
    timestamp TIMESTAMPTZ,
    --years_to_graduate is 0 for seniors, 1 for juniors, etc..
    years_to_graduate INTEGER,
    FOREIGN KEY(uid) REFERENCES users ON DELETE CASCADE,
    FOREIGN KEY(cid) REFERENCES companies ON DELETE CASCADE
);

CREATE TABLE ignore (
    sender VARCHAR(100) PRIMARY KEY,
    -- these booleans serve to provide context whether this ignore should be applied for company or recruiter parsing
    company INTEGER DEFAULT 0 NOT NULL,
    -- recruiter ignoring will be implemented in a separate PR
    recruiter INTEGER DEFAULT 0 NOT NULL 
);

CREATE TABLE stage_durations (
    cid INTEGER NOT NULL,
    stage INTEGER NOT NULL, -- -1 represents start-end duration
    duration FLOAT,
    num_stages INTEGER,
    min_date VARCHAR(10),
    max_date VARCHAR(10),
    FOREIGN KEY(cid) REFERENCES companies ON DELETE CASCADE,
    PRIMARY KEY(cid, stage)
);

CREATE TABLE company_suggestions (
    cid1 INTEGER NOT NULL,
    cid2 INTEGER NOT NULL,
    -- Order is an integer ranging from 1-3 (1 is highest priority suggestion)
    ord INTEGER NOT NULL,
    FOREIGN KEY(cid1) REFERENCES companies(cid) ON DELETE CASCADE,
    FOREIGN KEY(cid2) REFERENCES companies(cid) ON DELETE CASCADE
);

CREATE TABLE google_projects (
    gcid SERIAL PRIMARY KEY,
    project_id VARCHAR(40),
    topic VARCHAR(100),
    has_space INTEGER DEFAULT 1
);

CREATE TABLE gmail (
    uid INTEGER PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    token VARCHAR(256) NOT NULL UNIQUE,
    history VARCHAR(64),
    label VARCHAR(64) NOT NULL,
    gcid INTEGER,
    FOREIGN KEY(uid) REFERENCES users ON DELETE CASCADE,
    FOREIGN KEY(gcid) REFERENCES google_projects
);

CREATE TABLE trending_companies (
    cid INTEGER NOT NULL,
    FOREIGN KEY(cid) REFERENCES companies ON DELETE CASCADE
);

CREATE TABLE referrals (
    uid INTEGER PRIMARY KEY,
    points INTEGER DEFAULT 0 NOT NULL,
    redemptions INTEGER DEFAULT 0 NOT NULL,
    FOREIGN KEY(uid) REFERENCES users ON DELETE CASCADE
);

CREATE TABLE redeemed_recruiters (
    uid INTEGER,
    rid INTEGER NOT NULL,
    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP NOT NULL,
    FOREIGN KEY(uid) REFERENCES users ON DELETE CASCADE,
    FOREIGN KEY(rid) REFERENCES recruiters ON DELETE CASCADE
);

CREATE TABLE college_recruiter_link (
    college VARCHAR(100) NOT NULL,
    rid INTEGER NOT NULL,
    FOREIGN KEY(rid) REFERENCES recruiters ON DELETE CASCADE
);

CREATE OR REPLACE FUNCTION update_modified_column_timestamp()   
RETURNS TRIGGER AS $$
BEGIN
    NEW.timestamp = now();
    RETURN NEW;   
END;
$$ language 'plpgsql';

CREATE TRIGGER update_job_timestamp BEFORE UPDATE ON jobs FOR EACH ROW EXECUTE PROCEDURE update_modified_column_timestamp();
