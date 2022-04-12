from lxml import etree
import aiohttp

from m42pl.commands import GeneratingCommand
from m42pl.fields import Field, FieldsMap
from m42pl.event import derive


class WebScrape(GeneratingCommand):
    """Scrapes a website according to simple scraping rules.
    """

    _aliases_   = ['webscrape', 'web_scrape', 'webscrapper', 'web_scrapper']
    _syntax_    = '[url=]<base url> [articles=]<articles XPath> [iterator=]<iterator XPath>'

    def __init__(self, url: str, articles: list, iterator: str):
        """
        :param url:         Base URL
        :param articles:    XPath expression(s) to extract articles
        :param iterator:    XPath expression(s) to get next index page
        """
        super().__init__(url, articles, iterator)
        self.fields = FieldsMap(
            url=Field(url, type=str),
            articles=Field(articles, type=str),
            iterator=Field(iterator, type=str)
        )
        self.xml_parser = etree.HTMLParser()

    async def setup(self, event, pipeline):
        self.fields = await self.fields.read(event, pipeline)
        # Build articles' XPath expressions
        self.articles_xpath = etree.XPath(self.fields.articles)
        # Build iterator's XPath expressions
        self.iterator_xpath = etree.XPath(self.fields.iterator)

    def scrape_articles(self, tree):
        _articles = []
        for article in self.articles_xpath(tree):
            try:
                _articles.append({
                    'attrs': dict(getattr(article, 'attrib', {})),
                    'text': getattr(article, 'text', '')
                })
            except Exception:
                pass
        return _articles

    def scrape_iterator(self, tree):
        try:
            return self.iterator_xpath(tree)[0]
        except Exception:
            return None

    async def target(self, event, pipeline):
        nextpage = self.fields.url
        async with aiohttp.ClientSession() as session:
            # Loop until there is no more 
            while nextpage is not None:
                async with session.get(nextpage) as response:
                    # Get response content
                    page_src = (await response.read()).decode('UTF-8')
                    # Parse response content as XML
                    page_tree = etree.fromstring(
                        page_src,
                        parser=self.xml_parser
                    )
                    # Backup current URL
                    currpage = nextpage
                    # Get articles and next page url
                    articles = self.scrape_articles(page_tree)
                    nextpage = self.scrape_iterator(page_tree)
                    # Yield one event per article
                    for article in articles:
                        yield derive(event, article)
