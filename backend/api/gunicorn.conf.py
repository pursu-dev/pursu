# pylint: disable=C0114,C0115
import logging
from gunicorn import glogging

class PursuMainLogger(glogging.Logger):
    def setup(self, cfg):
        super().setup(cfg)
        accessLogger = logging.getLogger("gunicorn.access")
        accessLogger.addFilter(MainAPIHealthCheckFilter())
        errorLogger = logging.getLogger("gunicorn.error")
        errorLogger.addFilter(MainAPIHealthCheckFilter())

class MainAPIHealthCheckFilter(logging.Filter):
    def filter(self, record):
        return 'GET /api/health' not in record.getMessage()

bind = '0.0.0.0:3000'
workers = 2
daemon = True
capture_output = True
loglevel = "debug"
errorlog = "../logs/main_api_logs"
logger_class = PursuMainLogger
