import exceptions

from scrapy.contrib.spiders import CrawlSpider
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
import httplib2

from PodSearchBot.items import PodSearchBotItem

from Resource import PathTool
from Resource import Resource


class Digitalpodcast_com(CrawlSpider):

    start_urls = ["http://api.digitalpodcast.com/opml/digitalpodcastalpha.opml"]    # public for scrapy
    
    _pt = PathTool.PathTool()

    _url = Resource(start_urls[0], "directory")
    _baseUrl = _url.getBaseUrl()
    name = _url.getSpiderName()                             # public for scrapy
    feed_list_path = _url.getPath()                         # public for scrapy

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        #podcast_urls_xpath = "/opml/body/outline/outline/@url"
        podcast_urls_xpath = "//outline/@url"
        links = hxs.select(podcast_urls_xpath).extract()
        print links
        for link in links:
            if link.startswith('/'):
                link = self._baseUrl + link
            item = PodSearchBotItem()
            item['link'] = link
            yield item
