import scrapy


class CssPapersSpider(scrapy.Spider):
    name = "css_papers"
    allowed_domains = ["dblp.org", "dl.acm.org"]
    start_urls = ["https://dblp.org/search/publ/api?q=toc%3Adb/conf/ccs/ccs2023.bht%3A&h=1000&format=json"]

    def parse(self, response):
        pass
