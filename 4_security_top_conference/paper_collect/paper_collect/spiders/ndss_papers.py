import scrapy

class NdssSpider(scrapy.Spider):
    name = 'ndss'
    start_urls = ['https://www.ndss-symposium.org/ndss2024/accepted-papers/']  # 假设这是 NDSS 论文的页面链接
    year = '2024'

    def parse(self, response):
        # 获取所有论文条目
        for paper in response.css('div.tag-box.rel-paper'):
            # 提取论文的详细页面链接（'href' 属性）
            full_url = paper.css('a.paper-link-abs::attr(href)').get()

            # 跟踪论文详情页面，继续抓取论文的详细信息
            if full_url:  # 确保 full_url 被成功提取
                yield response.follow(full_url, self.parse_paper_details)

    def parse_paper_details(self, response):
        # 获取论文的标题、作者、摘要和PDF链接
        title = response.xpath('//h1[@class="entry-title"]/text()').get()
        authors = response.xpath('//div[@class="paper-data"]/p/strong/text()').get()
        # 获取摘要：移除 <strong> 标签的文本
        abstract = " ".join(response.xpath('//div[@class="paper-data"]/p//text()[not(ancestor::strong)]').getall()).strip()
        pdf_link = response.xpath('//div[@class="paper-buttons"]//a[contains(@href, "paper.pdf")]/@href').get()

        # 返回论文详细信息
        yield {
            'title': title,
            'authors': authors.strip() if authors else None,
            'abstract': abstract.strip() if abstract else None,
            'pdf_link': pdf_link if pdf_link else None,
            'year': self.year,
            'source': 'ndss'
        }
