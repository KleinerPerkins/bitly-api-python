import hashlib
import json
import sys
import time
import requests
import types
import warnings

GET = 'GET'
POST = 'POST'
PATCH = 'PATCH'

try:
    from urllib.request import build_opener, HTTPRedirectHandler
    from urllib.parse import urlencode
    from urllib.error import URLError, HTTPError
    string_types = str,
    integer_types = int,
    numeric_types = (int, float)
    text_type = str
    binary_type = bytes
except ImportError as e:
    from urllib2 import build_opener, HTTPRedirectHandler, URLError, HTTPError
    from urllib import urlencode
    string_types = basestring,
    integer_types = (int, long)
    numeric_types = (int, long, float)
    text_type = unicode
    binary_type = str


class DontRedirect(HTTPRedirectHandler):
    def redirect_response(self, req, fp, code, msg, headers, newurl):
        if code in (301, 302, 303, 307):
            raise HTTPError(req.get_full_url(), code, msg, headers, fp)


class Error(Exception):
    pass


class BitlyError(Error):
    def __init__(self, code, message):
        Error.__init__(self, message)
        self.code = code


def _utf8(s):
    if isinstance(s, text_type):
        s = s.encode('utf-8')
    assert isinstance(s, binary_type)
    return s


def _utf8_params(params):
    """encode a dictionary of URL parameters (including iterables) as utf-8"""
    assert isinstance(params, dict)
    encoded_params = []
    for k, v in params.items():
        if v is None:
            continue
        if isinstance(v, numeric_types):
            v = str(v)
        if isinstance(v, (list, tuple)):
            v = [_utf8(x) for x in v]
        else:
            v = _utf8(v)
        encoded_params.append((k, v))
    return dict(encoded_params)


class Connection(object):
    """
    This is a python library for accessing the bitly api
    http://github.com/bitly/bitly-api-python

    Usage:
        import bitly_api
        c = bitly_api.Connection('bitlyapidemo','R_{{apikey}}')
        # or to use oauth2 endpoints
        c = bitly_api.Connection(access_token='...')
        c.shorten('http://www.google.com/')
    """

    def __init__(self, login=None, api_key=None, access_token=None,
                 secret=None):
        self.host = 'https://api-ssl.bit.ly'
        self.login = login
        self.api_key = api_key
        self.access_token = access_token
        self.secret = secret
        (major, minor, micro, releaselevel, serial) = sys.version_info
        parts = (major, minor, micro, '?')
        self.user_agent = "Python/%d.%d.%d bitly_api/%s" % parts

        self._headers = {
            'User-agent': self.user_agent + ' urllib',
            'Authorization': 'Bearer {0}'.format(self.access_token)
        }

    def bitlink(self, bitlink):
        """query for a bitly link based on a long url (or list of long urls)"""
        return self._get('/v4/bitlinks/{0}'.format(bitlink))

    def shorten(self, uri, preferred_domain=None, group_guid=None):
        """ creates a bitly link for a given long url
        @parameter uri: long url to shorten
        @parameter preferred_domain: bit.ly[default], bitly.com, or j.mp
        """

        payload = {
            'long_url': uri
        }

        if preferred_domain:
            payload['domain'] = preferred_domain
        if group_guid:
            payload['group_guid'] = group_guid

        data = self._post('/v4/shorten', payload=payload)
        return data

    def group_bitlinks(self, group_guid, query=None, size=50, page=1):
        parmas = {
            'size': size,
            'page': page
        }

        if query:
            parmas['query'] = query

        links = []
        result = self._get('/v4/groups/{0}/bitlinks'.format(group_guid), params=parmas)

        for link in result['links']:
            links.append(link)

        if result['pagination']['next']:
            links.append(self.group_bitlinks(group_guid, query, size, result['pagination']['next']))

        return links

    def link_lookup(self, long_url, links):

        # since the passed in links param as return result of bit links, use python list comprehession to create a
        # dict by long_url
        link_dict = {i['long_url']: i for i in links}

        if long_url in link_dict:
            return link_dict[long_url]

        return None

    def _get(self, url, params=None):
        try:
            response = requests.get(self.host + url, headers=self._headers, params=params)
            code = response.status_code
            body = response.content.decode('utf-8')
            if code != 200:
                raise BitlyError(500, body)

            if not body.startswith('{'):
                raise BitlyError(500, body)

            data = json.loads(body)
            return data

        except URLError as e:
            raise BitlyError(500, str(e))
        except HTTPError as e:
            raise BitlyError(e.code, e.read())
        except BitlyError:
            raise
        except Exception:
            raise BitlyError(None, sys.exc_info()[1])

    def _post(self, url, payload):
        try:
            headers = self._headers
            headers['Content-Type'] = 'application/json'

            response = requests.post(self.host + url, headers=headers, json=payload)
            code = response.status_code
            body = response.content.decode('utf-8')
            if code >= 300:
                raise BitlyError(500, body)

            if not body.startswith('{'):
                raise BitlyError(500, body)

            data = json.loads(body)
            return data

        except URLError as e:
            raise BitlyError(500, str(e))
        except HTTPError as e:
            raise BitlyError(e.code, e.read())
        except BitlyError:
            raise
        except Exception:
            raise BitlyError(None, sys.exc_info()[1])

    def _call(self, host, method, params=None, secret=None, timeout=5000):
        if params:
            params['format'] = params.get('format', 'json')  # default to json

        if self.access_token:
            scheme = 'https'
            # params['access_token'] = self.access_token
            host = self.ssl_host

        if secret:
            # params['signature'] = self._generateSignature(params, secret)
            pass

        # force to utf8 to fix ascii codec errors
        if params:
            params = _utf8_params(params)

        request = None

        if not params:
            request = "%(scheme)s://%(host)s/%(method)s" % {
                'scheme': scheme,
                'host': host,
                'method': method
            }
        else:
            request = "%(scheme)s://%(host)s/%(method)s?%(params)s" % {
                'scheme': scheme,
                'host': host,
                'method': method,
                'params': urlencode(params, doseq=1)
            }

        try:
            opener = build_opener(DontRedirect())

            opener.addheaders = [
                ('User-agent', self.user_agent + ' urllib'),
                ('Authorization', 'Bearer {0}'.format(self.access_token))
            ]

            response = opener.open(request)
            code = response.code
            result = response.read().decode('utf-8')
            if code != 200:
                raise BitlyError(500, result)
            if not result.startswith('{'):
                raise BitlyError(500, result)
            data = json.loads(result)
            if data.get('status_code', 500) != 200:
                raise BitlyError(data.get('status_code', 500),
                                 data.get('status_txt', 'UNKNOWN_ERROR'))
            return data
        except URLError as e:
            raise BitlyError(500, str(e))
        except HTTPError as e:
            raise BitlyError(e.code, e.read())
        except BitlyError:
            raise
        except Exception:
            raise BitlyError(None, sys.exc_info()[1])