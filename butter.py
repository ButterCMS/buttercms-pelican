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
        DEFAULT_CATEGORY = self.settings.get('DEFAULT_CATEGORY')
        baseReader = BaseReader(self.settings)

        butter_posts = []
        page = 1
        while True:
            # Paginate through all pages
            result = self.client.posts.all({'page_size': 10, 'page': page})
            if 'data' in result:
                butter_posts.extend(result['data'])

            if 'meta' in result and 'next_page' in result['meta'] and result['meta']['next_page']:
                page += 1
            else:
                break
        all_articles = []
        counter = 0
        for post in butter_posts:
            if post['status'] == 'published':
                counter += 1
                logger.info('GET TO article: %s' % post['title'])
                logger.info('counter: %s' % str(counter))
                datestr = post['published'] if 'published' in post else post['created']
                date = parser.parse(datestr)
                title = post['title']
                content = post['body']
                author = post['author']['first_name']
                authorObject = baseReader.process_metadata('author', author)
                slug = post['slug'] if 'slug' in post else None
                logger.info('--HAS slug: %s' % str(slug))
                categoryObj = None
                if post['categories']:
                    category = post['categories'][0]['name']
                else:
                    category = DEFAULT_CATEGORY
                categoryObj = baseReader.process_metadata('category', category)

                metadata = {'title': title,
                            'date': date,
                            'category': categoryObj,
                            'authors': [authorObject]}
                if slug:
                    metadata['slug'] = slug


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

        logger.info('++++++++++++++++++++++++++++++++++++')
        logger.info('GOT categories %s' % str(self.categories))
        logger.info('++++++++++++++++++++++++++++++++++++')

        self._update_context(('articles', 'dates', 'categories', 'authors'))
        # Disabled for 3.3 compatibility for now, great.
        # self.save_cache()
        # self.readers.save_cache()

        # And finish.
        # signals.article_generator_finalized.send(self)

    # def generate_output(self, writer):
    #     # Intentionally leave this blank
    #     pass

    def generate_pages(self, writer):
        """Generate the pages on the disk"""
        write = partial(writer.write_file,
                        relative_urls=self.settings['RELATIVE_URLS'],
                        override_output=True)

        # to minimize the number of relative path stuff modification
        # in writer, articles pass first
        # self.generate_articles(write)
        self.generate_period_archives(write)
        self.generate_direct_templates(write)

        # and subfolders after that
        self.generate_categories(write)
        self.generate_authors(write)


def get_generators(pelican_object):
    return ButterGenerator


def register():
    signals.get_generators.connect(get_generators)
