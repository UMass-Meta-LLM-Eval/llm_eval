import logging
import io

from .constants import PROGRESS

class TqdmToLogger(io.StringIO):
    logger: logging.Logger = None
    level = None
    buf = ''
    def __init__(self,logger,level=PROGRESS):
        super().__init__()
        self.logger: logging.Logger = logger
        self.level = level or logging.INFO

    def write(self,buf):
        self.buf = buf.strip('\r\n\t ')

    def flush(self):
        self.logger.log(self.level, self.buf)
