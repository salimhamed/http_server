import socket
import sys
import os
import mimetypes


CRLF = '\r\n'
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
WEBROOT = os.path.join(BASE_DIR, 'webroot')


def response_ok(body, mimetype):
    """returns a HTTP response"""
    if body is not None and mimetype is not None:
        resp = []
        resp.append("HTTP/1.1 200 OK")
        resp.append("Content-Type: {}".format(mimetype))
        resp.append("")
        resp.append(body)
    else:
        raise NameError
    return CRLF.join(resp)


def response_not_found():
    """returns a 405 Not Found response"""
    resp = []
    resp.append("HTTP/1.1 404 Not Found")
    resp.append("")
    return CRLF.join(resp)


def response_method_not_allowed():
    """returns a 405 Method Not Allowed response"""
    resp = []
    resp.append("HTTP/1.1 405 Method Not Allowed")
    resp.append("")
    return CRLF.join(resp)


def parse_request(request):
    first_line = request.split(CRLF, 1)[0]
    method, uri, protocol = first_line.split()
    if method != "GET":
        raise NotImplementedError("We only accept GET")
    print >>sys.stderr, 'request is okay'
    return uri


def resolve_uri(uri):
    """
    Looks up a resource on disk using the URI and returns that resource.
    """
    # map the pathname represented by the URI to a filesystem location
    resource = os.path.join(WEBROOT, uri.lstrip('/'))

    # if the URI is a directory, it should return a plain-text listing and the
    # mimetype 'text-plain'
    if os.path.isdir(resource):
        content = '\n'.join(os.listdir(resource))
        type = 'text/plain'

    # if the URI is a file, it should return the contents of that file and its
    # correct mimetype
    elif os.path.isfile(resource):
        with open(resource, 'rb') as f:
            content = f.read()
        type = mimetypes.guess_type(resource)[0]

    # if the URI does not map to a real location, it should raise an exception
    # that the server can catch to return a 404 response
    else:
        raise ValueError

    return content, type


def server():
    address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print >>sys.stderr, "making a server on %s:%s" % address
    sock.bind(address)
    sock.listen(1)

    try:
        while True:
            print >>sys.stderr, 'waiting for a connection'
            conn, addr = sock.accept()  # blocking
            try:
                print >>sys.stderr, 'connection - %s:%s' % addr
                request = ""
                while True:
                    data = conn.recv(1024)
                    request += data
                    if len(data) < 1024 or not data:
                        break

                try:
                    uri = parse_request(request)
                except NotImplementedError:
                    response = response_method_not_allowed()
                else:
                    try:
                        content, type = resolve_uri(uri)
                        response = response_ok(content, type)
                    except (NameError, ValueError):
                        response = response_not_found()

                print >>sys.stderr, 'sending response'
                conn.sendall(response)
            finally:
                conn.close()

    except KeyboardInterrupt:
        sock.close()
        return


if __name__ == '__main__':
    server()
    sys.exit(0)
