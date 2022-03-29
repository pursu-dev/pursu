# pylint: disable=C0114,C0115
import logging
from gunicorn import glogging

class PursuEmailLogger(glogging.Logger):
    def setup(self, cfg):
        super().setup(cfg)
        accessLogger = logging.getLogger("gunicorn.access")
        accessLogger.addFilter(EmailAnalysisHealthCheckFilter())
        errorLogger = logging.getLogger("gunicorn.error")
        errorLogger.addFilter(EmailAnalysisHealthCheckFilter())

class EmailAnalysisHealthCheckFilter(logging.Filter):
    def filter(self, record):
        return 'GET /api/email_analysis/health' not in record.getMessage()

bind = '0.0.0.0:4000'
workers = 2
daemon = True
capture_output = True
loglevel = "debug"
errorlog = "../logs/data_email_logs"
logger_class = PursuEmailLogger
