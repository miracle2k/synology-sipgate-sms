#!/usr/bin/env python

# Werkzeug is in a submodule, we don't need to bother about
# installing it separately on the NAS.
import sys
from os.path import join, dirname
sys.path.insert(0, join(dirname(__file__), 'werkzeug'))


try:
    import config
except ImportError:
    raise RuntimeError("no config")


from werkzeug import Request, Response
from werkzeug.exceptions import BadRequest, NotFound
import sipgateapi
import xmlrpclib


def send_sms(request):
    try:
        user = request.args['user']
        password = request.args['password']
        number = request.args['to']
        message = request.args['text']
    except KeyError:
        raise BadRequest("Missing url parameter")

    api = sipgateapi.SipgateAPI(user, password)
    try:
        api.send_sms(number, message)
    except sipgateapi.SanityCheckError, e:
        raise BadRequest('API call not sane: %s' % e)
    except xmlrpclib.ProtocolError, e:
        raise BadRequest('API call error: %s' % e)
    else:
        return Response('ok')


def app(environ, start_response):
    """The URL we receive must look something like this:

    http://localhost:10288/?user=FOO&password=BAR&to=12345&text=Hello+World
    """
    request = Request(environ)
    if request.path != '/':
        raise NotFound()

    try:
        return send_sms(request)(environ, start_response)
    except Exception, e:
        print e
        raise


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', config.PORT, app,
               use_reloader=False,
               use_debugger=False,
               use_evalex=False,
               extra_files=None,
               reloader_interval=1,
               threaded=False,
               processes=1,
               request_handler=None,
               static_files=None,
               passthrough_errors=False,)