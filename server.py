import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.httpclient import AsyncHTTPClient
from tornado.options import define, options

import os.path

define("port", default=3000, help="run on the given port", type=int)

class EmptyPageHandler(tornado.web.RequestHandler):
    def get(self):
        info = "Try the following {}".format([ i[0] for i in urls ])
        self.render("main.html", context_info=info)


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
            http_client = AsyncHTTPClient()
            http_client.fetch(
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
    """Using generator-based interface (tornado.gen)"""
    @tornado.gen.coroutine
    def get(self):
        url = "https://api.privatbank.ua/p24api/"
        url += "pubinfo?json&exchange&coursid=11"
        http_client = AsyncHTTPClient()
        http_response = yield http_client.fetch(url, validate_cert=False)
        self.write(http_response.body)
        self.set_header('Content-Type', 'application/json')


urls = [
    (r"/check", LinkCheckerHandler),
    (r"/kurs", CurrencyExchangeHandler),
    (r"/", EmptyPageHandler),
]

if __name__ == "__main__":
    try:
        print "Starting tornado web server"
        tornado.options.parse_command_line()
        app = tornado.web.Application(
            handlers=urls,
            debug=False,
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
        )
        http_server = tornado.httpserver.HTTPServer(app)
        http_server.listen(options.port)
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        tornado.ioloop.IOLoop.instance().stop()