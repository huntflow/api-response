#!/usr/bin/python3.7
# -*- coding: utf-8 -*-
import os

import tornado.ioloop
import tornado.web
import tornado.httpclient
import tornado.netutil
from tornado.options import options
import tornado.platform.caresresolver
from tort.logger import configure_logging

from handler import IndexHandler
import config


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (options.base_path or "/", IndexHandler),
        ]

        settings = dict(
            xsrf_cookies=True,
            debug=options.debug,
            cookie_secret="<MAKE YOUR SECRET>",
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            static_url_prefix=options.base_path + "/static/",
        )

        tornado.web.Application.__init__(self, handlers, **settings)


def make_app():
    configure_logging(options.log_filename, options.log_level)

    tornado.httpclient.AsyncHTTPClient.configure(
        "tornado.simple_httpclient.SimpleAsyncHTTPClient", max_clients=50
    )
    tornado.netutil.Resolver.configure("tornado.platform.caresresolver.CaresResolver")

    return Application()


if __name__ == "__main__":
    tornado.options.parse_command_line()

    app = make_app()

    app.listen(options.port, options.host)

    tornado.ioloop.IOLoop.current().start()
