from scrapy.contrib.spiders import CrawlSpider
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector

from PodSearchBot.items import PodsearchbotItem

from Util.PathTool.PathTool import PathTool
from Resource.Resource import Resource


class Podster_de(CrawlSpider):

    start_urls = ["http://podster.de/tag/system:all"]       # public for scrapy
    
    _pt = PathTool()

    _url = Resource(start_urls[0], "directory")
    _baseUrl = _url.get_base_url()
    name = _url.get_spider_name()                             # public for scrapy
    feed_list_path = '../' + _url.get_path()                 # public for scrapy

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        
        next_page_xpath = "//tr/td[3]/a/@href"
        next_page_urls = hxs.select(next_page_xpath).extract()
        if not next_page_urls: return 
        next_page_url = next_page_urls[0]
        yield Request(next_page_url, callback=self.parse)
        
        podcast_page_xpath = "//table[@class='podcasts']//tr[2]/td[1]/a/@href"
        podcast_page_urls = hxs.select(podcast_page_xpath).extract()
        for podcast_page_url in podcast_page_urls:
            yield Request(podcast_page_url, callback=self.parse_podcast_page)

    def parse_podcast_page(self, response):
        hxs = HtmlXPathSelector(response)      
        item = PodsearchbotItem()

        try:
            podcast_url_xpath = "//div[@id='content']//a[5]/@href"
            link = hxs.select(podcast_url_xpath).extract()[0]
            if not link.startswith('/community/map;show=') and \
               not link.startswith('http://podster.de/view/'):
                item['link'] = link
        except IndexError:
            pass
        try:
            podcast_url_xpath = "//div[@id='content']//a[4]/@href"
            link = hxs.select(podcast_url_xpath).extract()[0]
            if not link.startswith('/community/map;show=') and \
               not link.startswith('http://podster.de/view/'):
                item['link'] = link
        except IndexError:
            pass
        try:
            podcast_url_xpath = "//div[@id='content']//div[@class='boxcontent']/a[2]/@href"
            link = hxs.select(podcast_url_xpath).extract()[0]            
            if not link.startswith('/community/map;show=') and \
               not link.startswith('http://podster.de/view/'):
                item['link'] = link
        except IndexError:
            pass
        try:
            link = item['link']
        except KeyError:
            print(('PodsterDe: WARNING: The page %s did not contain a link to a feed.' % response.url))
            return
        yield item
