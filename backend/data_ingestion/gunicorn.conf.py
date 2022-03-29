# pylint: disable=C0114,C0115
import logging
from gunicorn import glogging


class PursuDataLogger(glogging.Logger):
    def setup(self, cfg):
        super().setup(cfg)
        accessLogger = logging.getLogger("gunicorn.access")
        accessLogger.addFilter(DataIngestionHealthCheckFilter())
        errorLogger = logging.getLogger("gunicorn.error")
        errorLogger.addFilter(DataIngestionHealthCheckFilter())


class DataIngestionHealthCheckFilter(logging.Filter):
    def filter(self, record):
        return 'GET /api/data_ingestion/health' not in record.getMessage()


bind = '0.0.0.0:2000'
workers = 2
daemon = True
capture_output = True
loglevel = "debug"
errorlog = "../logs/data_email_logs"
logger_class = PursuDataLogger
timeout = 120
