from scrapy.spider import BaseSpider
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector

from Scrapy.items import PodcastFeedItem

from PathTool import PathTool
from UrlTool import UrlTool


class Podster_de(BaseSpider):

    start_urls = ["http://podster.de/tag/system:all"]
    
    _ut = UrlTool()
    _pt = PathTool()

    _baseUrl = _ut.getBaseUrl(start_urls[0])
    name = _ut.getSpiderName(start_urls[0]) # needs to be public for scrapy
    feedListPath = _pt.getFeedListPath(start_urls[0])

    def parse(self, response):
        yield Request(response.url, callback=self.parse_sitemapPage)
        hxs = HtmlXPathSelector(response)
        nextPageXpath = "//tr/td[3]/a/@href"
        nextPageUrls = hxs.select(nextPageXpath).extract()
        if not nextPageUrls: return 
        nextPageUrl = nextPageUrls[0]
        if nextPageUrl.endswith("20"): return
        yield Request(nextPageUrl, callback=self.parse)

    def parse_sitemapPage(self, response):
        hxs = HtmlXPathSelector(response)
        podcastPageXpath = "//table[@class='podcasts']//tr[2]/td[1]/a/@href"
        podcastPageUrls = hxs.select(podcastPageXpath).extract()
        for podcastPageUrl in podcastPageUrls: 
            yield Request(podcastPageUrl, callback=self.parse_podcastPage)

    def parse_podcastPage(self, response):
        hxs = HtmlXPathSelector(response)
        podcastTitleXpath = "//div[@id='caption-header']"
        podcastUrlXpath = "/html/body/div[@id='god_container']/div[@id='main_container']/div[@id='content']/div[@class='sidecol left large']/div[@class='box']/div[@class='boxcontent']/a[2]"
        
        try:
            item = PodcastFeedItem()
            item['title'] = hxs.select(podcastTitleXpath).extract()[0]
            item['link'] = hxs.select(podcastUrlXpath).extract()[0]
            print item['title'], item['link']
        except IndexError:
            return

        yield item