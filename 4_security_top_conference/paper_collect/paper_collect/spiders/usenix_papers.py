import scrapy

class UsenixSpider(scrapy.Spider):
    name = 'usenix'
    start_urls = ['https://www.usenix.org/conference/usenixsecurity24/fall-accepted-papers']
    year = '2024'

    def parse(self, response):
        # 获取所有的论文信息
        # 修改选择器以匹配实际的HTML结构
        for paper in response.css('article.node.node-paper.view-mode-schedule'):
            # 获取h2标签中的链接元素
            title_link = paper.css('h2 a')
            title = title_link.css('::text').get()
            relative_path = title_link.css('::attr(href)').get()

            # 确保找到了标题和链接
            if title and relative_path:
                # 论文详情页的完整URL
                full_url = response.urljoin(relative_path)

                # 跟踪链接并解析详细内容
                yield response.follow(full_url, self.parse_paper_details, meta={'title': title, 'relative_path': relative_path})

    def parse_paper_details(self, response):
        # 从 meta 中获取标题和相对路径
        title = response.meta['title']
        
        # 获取摘要和 PDF 链接
        # 获取作者信息 - 提取来自field-paper-people-text字段的文本
        authors_content = response.css('div.field-name-field-paper-people-text ::text').getall()
        authors = " ".join([text.strip() for text in authors_content if text.strip()])
        
        # 获取论文描述/摘要 - 从field-paper-description字段提取
        text_content = response.css('div.field-name-field-paper-description ::text').getall()
        abstract = " ".join([text.strip() for text in text_content if text.strip()])
        
        # 获取 PDF 链接 - 寻找PDF图标对应的链接
        pdf_link = response.css('span.usenix-schedule-media.pdf a::attr(href)').get()
        
        # 如果找不到PDF链接，尝试其他可能的位置
        if not pdf_link:
            pdf_link = response.css('div.field-name-field-final-paper-pdf a::attr(href)').get()

        yield {
            'title': title,
            'authors': authors,
            'abstract': abstract,
            'pdf_link': response.urljoin(pdf_link) if pdf_link else None,
            # 'url': response.url,  # 论文详情页的URL
            'year': self.year,
            'source': 'usenix'
        }