# -*- coding: utf-8 -*-

from main.models import *


class ArticleObject:

    def __init__(self, title='title', slug_name='slug_name',
                 content='content', morecontent='morecontent', pub_date='',
                 author='', category='', posted=False,
                 twit=False, tags=[], absolute_url='',
                 short_url='', rfc822_date=''):
        self.title = title
        self.slug_name = slug_name
        self.content = content
        self.morecontent = morecontent
        self.pub_date = pub_date
        self.author = author
        self.category = category
        self.posted = posted
        self.twit = twit
        self.tags = tags
        self.absolute_url = absolute_url
        self.short_url = short_url
        self.rfc822_date = rfc822_date

    def __repr__(self):
        return self.title

    def dict(self):
        return {"title": self.title,
                "slug_name": self.slug_name,
                "content": self.content,
                "morecontent": self.morecontent,
                "pub_date": self.pub_date,
                "author": self.author,
                "category": self.category,
                "posted": self.posted,
                "twit": self.twit,
                "tags": self.tags,
                "absolute_url": self.absolute_url,
                "short_url": self.short_url,
                "rfc822_date": self.rfc822_date, }


class ArticleList:

    def __init__(self):
        self.data = []

    def add(self, x):
        if type(ArticleObject()) == type(x):
            self.data.append(x)
        else:
            print("Проверьте тип переменной, должно быть" +
                  "экземпляром класса ArticleObject()")

    def __repr__(self):
        return repr('Всего элементов: ' + str((len(self.data))))

all = Article.objects.select_related().all()
Articles = ArticleList()

for x in all:
    post = ArticleObject()
    post.title = x.title
    post.slug_name = x.slug_name
    post.content = x.content
    post.morecontent = x.morecontent
    post.pub_date = x.pub_date
    post.author = x.author.get()
    post.category = x.category.get()
    post.posted = x.posted
    post.twit = x.twit
    post.tags = x.tags
    post.absolute_url = x.get_absolute_url
    post.short_url = x.get_short_url
    post.rfc822_date = x.get_rfc822_date
    Articles.add(post)

connection = Connection('localhost', 27017)
db = connection['ukrgadget']
collection = db['Articles']

collection.insert(Articles.data)
