import sys
import logging
import os
from bitly_api import v4Connection as Connection


from dotenv import load_dotenv

load_dotenv('.env')

log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG, format=log_format)
logger = logging.getLogger(__name__)

BITLY_DOMAIN = os.environ['BITLY_DOMAIN']
BITLY_GROUP_GUID = ''

if __name__ == '__main__':

    logger.debug('Logger Initialized')
    logger.debug('Testing Bitly Api wrapper')

    bitly = Connection(access_token=os.environ['BITLY_ACCESS_TOKEN'])

    bitlink = bitly.bitlink('kpiq.io/2NyA91a')

    links = bitly.group_bitlinks(BITLY_GROUP_GUID, query='http://www.example.com')

    link = bitly.link_lookup('http://www.example.com/', links)

    logger.debug('Bitly Search Results:')
    logger.debug(links)

    short_url = bitly.shorten('http://www.example.com', BITLY_DOMAIN, BITLY_GROUP_GUID)

    logger.debug('Short URL:')
    logger.debug(short_url)

    pass
