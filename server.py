import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.httpclient import AsyncHTTPClient
from tornado.options import define, options

import ujson as json

define("port", default=3000, help="run on the given port", type=int)


class LinkCheckerHandler(tornado.web.RequestHandler):
    """Using callbacks"""

    @tornado.web.asynchronous
    def get(self):
        url = self.get_argument('url', None)
        if url is None:
            host = self.request.host
            to_response = "Example of usage : </br>"
            to_response += "http://{}/check?url=https://ya.ru".format(host)
            self.write(to_response)
            self.finish()
        if url is not None:
            client = AsyncHTTPClient()
            client.fetch(
                url,
                method='GET',
                callback=self.on_response,
                validate_cert=False,
            )


    def on_response(self, response):
        if response.code == 200:
            to_response = {'response_code': 200, "accessible": True}
            to_response['request_time'] = response.request_time
            to_response['headers'] = {
                x:y for x,y in response.headers.get_all()
            }
            self.write(to_response)
            self.finish()
        if response.code != 200:
            to_response = {'response': response.code, "accessible": False}
            self.write(to_response)
            self.finish()


class CurrencyExchangeHandler(tornado.web.RequestHandler):
    """Using generators. Will be implemented soon"""

    def get(self):
        self.write(self.request.host)


urls = [
    (r"/check", LinkCheckerHandler),
    (r"/kurs", CurrencyExchangeHandler),
]

if __name__ == "__main__":
    print "Starting tornado web server"
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=urls, debug=True)
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()