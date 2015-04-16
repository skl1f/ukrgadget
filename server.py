import tornado.ioloop
import tornado.web
import os
import tornado.template
from tornado.options import define, options
from tornado.template import Template, Loader
from pymongo import Connection, errors
from ukrgadget.db import convert_to_json
from ukrgadget.model import ArticleObject
from time import strftime, strptime, gmtime
from bson.objectid import *

define('port', default=80, help='run on the given port', type=int)


class Application(tornado.web.Application):

    def __init__(self):
        try:
            conn = Connection('127.0.0.1', 27017).ukrgadget
            conn.authenticate('skl1f', 'ukr')
            self.database = conn['Articles']
        except errors.AutoReconnect as er:
            print('Error database connection:', er)

        try:
            self.loader = Loader(
                "/home/skl1f/code/ukrgadget.com/templates")
        except:
            pass

        handlers = [
            # (r'/data.json', LongRequestHandler),
            # (r'/page/', PaginateRequestHandler),
            # (r'/page/([0-9]+)', PaginateRequestHandler),
            (r'/admin/edit/(.*)', EditHandler),
            (r'/', MainHandler),
            (r'/admin/list/', ListHandler),
            (r'/admin/list/([0-9]+)', ListHandler),
            (r'/admin/new/', NewHandler),
            (r'/admin/delete/(.*)', DeleteHandler),
            (r'/admin/post/(.*)', PostHandler),
            (r'/admin/twit/(.*)', TwitHandler),
        ]
        settings = dict(
            cookie_secret='43oETzKXQAGaYdk6fd8fG1kJFuYh7EQnp2XdTP1o/Vo=',
            template_path=os.path.join(os.path.dirname(__file__), 'templates'),
            static_path=os.path.join(os.path.dirname(__file__), 'static'),
            xsrf_cookies=True,
            autoescape=False,
            login_url='/admin/new/',
            # debug=True,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class LongRequestHandler(tornado.web.RequestHandler):

    def database_callback(self, *args, **kwargs):
        if not args[0]:
            self.finish()
        else:
            self.set_header("Content-Type", "application/json; charset=UTF-8")
            self.write(args[0])
            self.flush()
            self.finish()

    @tornado.web.asynchronous
    def get(self):
        data = self.application.database.find().sort("pub_date", -1)
        data = convert_to_json(data)
        render = Template("{% autoescape None %}{{ json_data }}").generate(
            json_data=data)
        tornado.ioloop.IOLoop.instance().add_callback(
            self.async_callback(self.database_callback, render))


class PaginateRequestHandler(tornado.web.RequestHandler):

    """docstring for PaginaRequestPage"""

    def list_callback(self, *args, **kwargs):
        self.set_header("Content-Type", "application/json; charset=UTF-8")
        self.write(args[0])
        self.flush()
        self.finish()

    @tornado.web.asynchronous
    def get(self, page=1):
        page = int(page)
        all_items = self.application.database.find().sort('pub_date', -1)
        all_items_count = all_items.count()
        items = list(range(-15, all_items_count, 15))
        list_items = list(range(items[page], items[page + 1]))
        list_articles = []
        for x in list_items:
            list_articles.append(all_items[x])
        list_articles = convert_to_json(list_articles)
        tornado.ioloop.IOLoop.instance().add_callback(
            self.async_callback(self.list_callback, list_articles))


class NewHandler(tornado.web.RequestHandler):

    def get(self):
        item = ArticleObject().dict()
        xsrf = self.xsrf_form_html()
        date = strftime("%m/%d/%Y", gmtime())
        rfc822_date = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())

        html_template = self.application.loader.load("editor.html")\
            .generate(title=item['title'],
                      slug_name=item['slug_name'],
                      content=item['content'],
                      morecontent=item['morecontent'],
                      pub_date=date,
                      author=item['author'],
                      category=item['category'],
                      posted=item['posted'],
                      twit=item['twit'],
                      tags=item['tags'],
                      absolute_url=item['absolute_url'],
                      short_url=item['short_url'],
                      rfc822_date=rfc822_date,
                      xsrf_input=xsrf,)
        self.write(html_template)

    def post(self, *args, **kwargs):
        art = ArticleObject()
        art.title = self.get_argument("title")
        art.slug_name = self.get_argument("uri")
        art.content = self.get_argument("content")
        art.morecontent = self.get_argument("morecontent")
        try:
            q = strptime(self.get_argument("pub_date"), "%m/%d/%Y")
            art.pub_date = strftime("%Y-%m-%d", q)
            art.rfc822_date = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        except:
            q = strptime(self.get_argument("pub_date"), "%Y-%m-%d")
            art.pub_date = self.get_argument("pub_date")
            art.rfc822_date = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        art.author = self.get_argument("name")
        art.category = self.get_argument("category")
        art.tags = self.get_argument("tags")
        art.posted = False
        art.twit = False
        art.absolute_url = 'http://ukrgadget/' + \
            self.get_argument("category") + '/' + self.get_argument("uri")
        art.short_url = 'http://ukrgadget.com/go/' + \
            str(self.application.database.find().count() + 1)
        ident = self.application.database.insert(art.dict())
        self.redirect('/admin/edit/' + str(ident), permanent=False, status=302)


class EditHandler(tornado.web.RequestHandler):

    def get(self, ident):
        item = self.application.database.find_one({"_id": ObjectId(ident)})
        if self.application.database.find({
                "slug_name": item['slug_name']}).count() == 1:
            xsrf = self.xsrf_form_html()
            q = strptime(item['pub_date'], "%Y-%m-%d")
            date = strftime("%m/%d/%Y", q)
            ident = item['_id']
            html_template = self.application.loader.load("edit_articles.html")\
                .generate(title=item['title'],
                          slug_name=item['slug_name'],
                          content=item['content'],
                          morecontent=item['morecontent'],
                          pub_date=date,
                          author=item['author'],
                          category=item['category'],
                          posted=item['posted'],
                          twit=item['twit'],
                          tags=item['tags'],
                          absolute_url=item['absolute_url'],
                          short_url=item['short_url'],
                          rfc822_date=rfc822_date,
                          xsrf_input=xsrf,)
            self.write(html_template)
        else:
            xsrf = self.xsrf_form_html()
            q = strptime(item['pub_date'], "%Y-%m-%d")
            date = strftime("%m/%d/%Y", q)
            ident = item['_id']
            html_template = self.application.loader.load("edit_articles.html")\
                .generate(title=item['title'],
                          slug_name=item['slug_name'],
                          content=item['content'],
                          morecontent=item['morecontent'],
                          pub_date=date,
                          author=item['author'],
                          category=item['category'],
                          posted=item['posted'],
                          twit=item['twit'],
                          tags=item['tags'],
                          absolute_url=item['absolute_url'],
                          short_url=item['short_url'],
                          rfc822_date=rfc822_date,
                          xsrf_input=xsrf,)
            self.write(html_template)

    def post(self, *args, **kwargs):
        art = ArticleObject()
        item = self.application.database.find_one(
            {"_id": ObjectId(self.get_argument("ident_form"))})
        art.title = self.get_argument("title")
        art.slug_name = self.get_argument("uri")
        art.content = self.get_argument("content")
        art.morecontent = self.get_argument("morecontent")
        try:
            q = strptime(self.get_argument("pub_date"), "%m/%d/%Y")
            art.pub_date = strftime("%Y-%m-%d", q)
            art.rfc822_date = strftime("%a, %d %b %Y %H:%M:%S +0000", q)
        except:
            q = strptime(self.get_argument("pub_date"), "%Y-%m-%d")
            art.pub_date = self.get_argument("pub_date")
            art.rfc822_date = strftime("%a, %d %b %Y %H:%M:%S +0000", q)
        art.author = self.get_argument("name")
        art.category = self.get_argument("category")
        art.tags = self.get_argument("tags")
        art.posted = item['posted']
        art.twit = item['twit']
        art.absolute_url = 'http://ukrgadget/' + \
            self.get_argument("category") + '/' + self.get_argument("uri")
        art.short_url = item['short_url']
        self.application.database.update(
            {"_id": ObjectId(self.get_argument("ident_form"))}, art.dict())
        self.redirect(
            '/admin/edit/' + self.get_argument("ident_form"),
            permanent=False, status=302)


class DeleteHandler(tornado.web.RequestHandler):

    def get(self, ident):
        self.application.database.remove({"_id": ObjectId(ident)}),
        self.redirect('/admin/list/', permanent=False, status=302)


class PostHandler(tornado.web.RequestHandler):

    def get(self, ident):
        art, item = self.application.database.find_one(
            {"_id": ObjectId(ident)}),\
            self.application.database.find_one({"_id": ObjectId(ident)})
        if self.application.database.find(
                {"slug_name": item['slug_name']}).count() == 1:
            art['posted'] = True
            self.application.database.update(item, art)
            self.redirect('/admin/list/', permanent=False, status=302)
        else:
            self.redirect('/admin/edit/' + ident, permanent=False, status=302)


class TwitHandler(tornado.web.RequestHandler):

    def get(self, ident):
        art, item = self.application.database.find_one(
            {"_id": ObjectId(ident)}),\
            self.application.database.find_one({"_id": ObjectId(ident)})
        art['twit'] = True
        self.application.database.update(item, art)
        self.redirect('/admin/list/', permanent=False, status=302)


class ListHandler(tornado.web.RequestHandler):

    """docstring for ListRequestPage"""

    def list_callback(self, *args, **kwargs):
        html_template = self.application.loader.load("list_articles.html")\
            .generate(articles=args[0],
                      paginator=args[1],
                      page=args[2],)
        self.write(html_template)
        self.flush()
        self.finish()

    @tornado.web.asynchronous
    def get(self, page=1):
        page = int(page)
        all_items = self.application.database.find().sort(
            [("pub_date", -1), ("short_url", 1)])
        all_items_count = all_items.count()
        items = list(range(-30, all_items_count + 30, 30))
        list_items = list(range(items[page], items[page + 1]))
        if ((all_items_count / 30) % round(all_items_count / 30) == 0.0):
            paginator = all_items_count / 30
        else:
            paginator = int(all_items_count / 30) + 1
        paginator = [1 + i for i in range(paginator)]
        list_articles = []
        for x in list_items:
            try:
                list_articles.append(all_items[x])
            except IndexError:
                pass
        tornado.ioloop.IOLoop.instance().add_callback(
            self.async_callback(self.list_callback,
                                list_articles, paginator, page))


class MainHandler(tornado.web.RequestHandler):

    """docstring for MainHandler"""

    def get(self):
        html_template = '''<!DOCTYPE HTML>
<html>
<head>
<title>Mustache Samples</title>
</head>

<body>
Olololo
</body>
</html>'''
        self.write(html_template)


def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    print('Server started on port %s' % options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
