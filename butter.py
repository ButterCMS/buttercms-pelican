from collections import defaultdict
import datetime
import logging

from pelican import signals

from operator import attrgetter, itemgetter
from functools import partial

from pelican.generators import ArticlesGenerator, Generator
from pelican.contents import Article, Page, Static
from pelican.utils import copy, process_translations, mkdir_p
from pelican.readers import BaseReader, Readers

from butter_cms import ButterCMS

from dateutil import parser


logger = logging.getLogger()


class ButterGenerator(ArticlesGenerator):
    def __init__(self, *args, **kwargs):
        """initialize properties"""
        self.articles = []  # only articles in default language
        self.translations = []
        self.dates = {}
        self.categories = defaultdict(list)
        self.authors = defaultdict(list)
        super(ButterGenerator, self).__init__(*args, **kwargs)

        # 'cause settings is initialized in super
        self.client = ButterCMS(self.settings.get('BUTTER_CONFIG')['api_key'])

    # Private helper function to generate
    def _generate_butter_articles(self):
        baseReader = BaseReader(self.settings)

        butter_result = self.client.posts.all()
        all_articles = []
        if 'data' in butter_result:
            posts = butter_result['data']
            for post in posts:
                if post['status'] == 'published':
                    datestr = post['published'] if 'published' in post else post['created']
                    date = parser.parse(datestr)
                    title = post['title']
                    content = post['body']
                    author = post['author']['first_name']
                    authorObject = baseReader.process_metadata('author', author)
                    slug = post['slug']
                    if post['categories']:
                        category = post['categories'][0]['name']
                    else:
                        category = ''
                    categoryObj = baseReader.process_metadata('category', category)

                    metadata = {'title': title,
                                'date': date,
                                'category': categoryObj,
                                'authors': [authorObject],
                                'slug': slug}

                    article = Article(content=content,
                                      metadata=metadata,
                                      settings=self.settings,
                                      context=self.context)

                    # # This seems like it cannot happen... but it does without fail.
                    article.author = article.authors[0]
                    all_articles.append(article)

        return all_articles

    def generate_context(self):
        # Update the context (only articles in default language)
        self.articles = self.context['articles']

        all_articles = []

        new_articles = self._generate_butter_articles()
        all_articles.extend(new_articles)

        # Continue with the rest of ArticleGenerator, code adapted from:
        # https://github.com/getpelican/pelican/blob/master/pelican/generators.py#L548

        # ARTICLE_ORDER_BY doesn't exist in 3.3, which was in Fedora 21.
        # (I wanted to be able to build this on F21 at the time).
        articles, translations = process_translations(all_articles)
        # , order_by=self.settings['ARTICLE_ORDER_BY'])
        self.articles.extend(articles)
        self.translations.extend(translations)

        # Disabled for 3.3 compatibility, great.
        # signals.article_generator_pretaxonomy.send(self)

        for article in self.articles:
            # only main articles are listed in categories and tags
            # not translations
            self.categories[article.category].append(article)
            if hasattr(article, 'tags'):
                for tag in article.tags:
                    self.tags[tag].append(article)
            for author in getattr(article, 'authors', []):
                self.authors[author].append(article)

        # This may not technically be right, but...
        # Sort the articles by date too.
        self.articles = list(self.articles)
        self.dates = self.articles
        self.dates.sort(key=attrgetter('date'),
                        reverse=self.context['NEWEST_FIRST_ARCHIVES'])

        # and generate the output :)

        # order the categories per name
        self.categories = list(self.categories.items())
        self.categories.sort(reverse=self.settings['REVERSE_CATEGORY_ORDER'])

        self.authors = list(self.authors.items())
        self.authors.sort()

        self._update_context(('articles', 'dates', 'categories', 'authors'))
        # Disabled for 3.3 compatibility for now, great.
        # self.save_cache()
        # self.readers.save_cache()

        # And finish.
        # signals.article_generator_finalized.send(self)

    def generate_output(self, writer):
        # Intentionally leave this blank
        pass


def get_generators(pelican_object):
    return ButterGenerator


def register():
    signals.get_generators.connect(get_generators)
