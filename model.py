from time import strftime, gmtime


class ArticleObject:

    def __init__(self, title='title', slug_name='slug_name', content='content',
                 morecontent='morecontent', author='name', category='',
                 tags=[], absolute_url='', short_url='',
                 pub_date='', twit=False, posted=False):
        self.title = title
        self.slug_name = slug_name
        self.content = content
        self.morecontent = morecontent
        self.pub_date = strftime("%Y-%m-%d", gmtime())
        self.author = author
        self.category = category
        self.posted = posted
        self.twit = twit
        self.tags = tags
        self.absolute_url = absolute_url
        self.short_url = ''
        self.rfc822_date = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())

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
