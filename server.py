#!/usr/bin/env python2.7

try:
    import config
except ImportError:
    raise RuntimeError("no config")


import logging
from urlparse import parse_qsl
import sipgateapi
import xmlrpclib


class BadRequest(Exception):
    pass


logger = logging.getLogger('sipgate-sms')


def send_sms(params, environ):
    try:
        user = params['user'].strip()
        password = params['password'].strip()
        number = params['to'].strip()
        message = params['text'].strip()
    except KeyError, e:
        raise BadRequest("Missing url parameter: %s" % e)

    logger.info('Request: user=%s, to=%s, message=%s' % (user, number, message))

    # Prepare some of the values
    if number[:1] == '+':
        number = number[2:]

    try:
        api = sipgateapi.SipgateAPI(user, password)
        api.send_sms(number, message)
    except sipgateapi.SanityCheckError, e:
        raise BadRequest('API call not sane: %s' % e)
    except xmlrpclib.ProtocolError, e:
        raise BadRequest('API call error: %s' % e)
    else:
        return 'ok'


def app(environ, start_response):
    """The URL we receive must look something like this:

    http://localhost:10288/?user=FOO&password=BAR&to=12345&text=Hello+World

    Note: The Synology Admin GUI validates the SMS provider URI, and in
    particular, expects the "text" parameter to have a certain format that
    I can't quite grasp and doesn't seem to be documented anywhere - some
    strings just seem to work, other not. "Hello+World", as in the example,
    does work.
    """
    if environ.get('PATH_INFO', '').lstrip('/').rstrip('/') != '':
        start_response('200 OK', [('Content-type', 'text/plain')])
        return ['error 404']

    try:
        response = send_sms(dict(parse_qsl(environ['QUERY_STRING'])), environ)
    except BadRequest, e:
        logger.error('Error: %s' % e)
        start_response('400 Bad Request', [('Content-type', 'text/plain')])
        return ['%s' % e]
    except Exception, e:
        logger.error('Error: %s' % e)
        raise
    else:
        logger.info('Success')
        start_response('200 Ok', [('Content-type', 'text/plain')])
        return [response]


def serve():
    from wsgiref.simple_server import make_server
    httpd = make_server('localhost', config.PORT, app)
    httpd.serve_forever()


if __name__ == '__main__':
    import sys
    import daemon

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    if len(sys.argv) == 2 and sys.argv[1] == '-d':
        handler = logging.FileHandler(config.LOGFILE)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        with daemon.DaemonContext(files_preserve=[handler.stream]):
            serve()
    else:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        serve()
