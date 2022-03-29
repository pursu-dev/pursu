INSERT INTO ignore
    (sender, company)
VALUES('jobs-noreply@linkedin.com', 1);
INSERT INTO ignore
    (sender, company)
VALUES('invitations@linkedin.com', 1);
INSERT INTO ignore
    (sender, company)
VALUES('jobs-listings@linkedin.com', 1);
INSERT INTO ignore
    (sender, company)
VALUES('messages-noreply@linkedin.com', 1);
INSERT INTO ignore
    (sender, company)
VALUES('linkedin@e.linkedin.com', 1);
INSERT INTO ignore
    (sender, recruiter)
VALUES('workflow.mail.us2.cloud.oracle.com', 1);
INSERT INTO ignore
    (sender, recruiter)
VALUES('icims', 1);

-- Mock google client credentials
INSERT INTO google_projects
    (project_id, topic)
VALUES('pursu_test_project', 'pursu_test_topic');
