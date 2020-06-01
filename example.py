import sys
import logging
import os
from bitly_api import Connection


from dotenv import load_dotenv

load_dotenv('.env')

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=log_format)
logger = logging.getLogger(__name__)

if __name__ == '__main__':

    logger.debug('Logger Initialized')
    logger.debug('Testing Bitly Api wrapper')

    bitly = Connection(access_token=os.environ['BITLY_ACCESS_TOKEN'])

    s = bitly.shorten('http://www.google.com')

    logger.debug('Bitly Search Results:')
    logger.debug(s)

    pass
