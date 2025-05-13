import scrapy

class AAAISpider(scrapy.Spider):
    name = "aaai"
    year = "2025"
    allowed_domains = ["aaai.org", "ojs.aaai.org"]
    # start_urls = ["https://aaai.org/proceeding/aaai-39-2025/"]

    # Define common headers that might be used by multiple request types
    # You can override these in specific requests if needed
    common_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/113.0.0.0 Safari/537.36',
        'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
    }

    def start_requests(self):
        urls = ["https://aaai.org/proceeding/aaai-39-2025/"]
        for url in urls:
            self.logger.info(f"Sending initial request to {url} with empty User-Agent")
            yield scrapy.Request(
                url,
                callback=self.parse,
                headers={'User-Agent': ''} # Set User-Agent to empty string here
            )

    def parse(self, response):
        self.logger.info(f"Parsing initial response from {response.url}")
        proceedings_links = response.css('div.archive-description a')
        for link in proceedings_links:
            href = link.attrib.get('href')
            if not href:
                self.logger.warning("Missing href on %r", link.get())
                continue
            section_url = response.urljoin(href)

            # Prepare headers for the section request
            section_headers = self.common_headers.copy()
            section_headers['Referer'] = response.url

            yield scrapy.Request(
                section_url,
                callback=self.parse_section_articles,
                dont_filter=True,
                headers=section_headers
            )

    def parse_section_articles(self, response):
        self.logger.info(f"Parsing section articles from {response.url}")
        list_items = response.css('ul.cmp_article_list.articles > li')
        if not list_items:
            self.logger.warning("No articles on %s", response.url)
            return

        for li in list_items:
            summary = li.css('div.obj_article_summary')
            if not summary:
                self.logger.warning(f"No summary found in list item on {response.url}")
                continue

            title_el = summary.css('h3.title a')
            title = title_el.css('::text').get(default='').strip()
            paper_page_url_relative = title_el.attrib.get('href')
            paper_page_url = response.urljoin(paper_page_url_relative) if paper_page_url_relative else None

            authors_list = summary.css('div.meta div.authors ::text').getall()
            authors = "、".join(x.strip() for x in authors_list if x and x.strip())

            pdf_relative_url = summary.css('ul.galleys_links a.pdf::attr(href)').get()
            pdf_url = response.urljoin(pdf_relative_url) if pdf_relative_url else None

            item = {
                'paper_title': title,
                'paper_url': paper_page_url,
                'authors': authors,
                'pdf_url': pdf_url,
                'source_section_url': response.url,
                'year': self.year,
                'source': 'aaai'
            }

            if paper_page_url:
                # Prepare headers for the paper detail page request
                paper_detail_headers = self.common_headers.copy()
                paper_detail_headers['Referer'] = response.url # Referer is the section page

                yield scrapy.Request(
                    paper_page_url,
                    callback=self.parse_paper_page,
                    meta={'item': item}, # Pass the partially filled item
                    headers=paper_detail_headers
                )
            else:
                self.logger.warning(f"No paper_url found for title: {title} on {response.url}")
                item['abstract'] = None # Or an empty string, or skip yielding
                yield item # Yield item without abstract if no paper_url

    def parse_paper_page(self, response):
        item = response.meta['item'] # Retrieve the item passed from previous request

        # Extract abstract
        # The abstract text is directly within the <section class="item abstract">
        # We need to get all text nodes, strip them, and join.
        abstract_parts = response.css('section.item.abstract ::text').getall()
        abstract = ' '.join(part.strip() for part in abstract_parts if part.strip()).strip()
        
        if not abstract: # Check if abstract is empty after stripping
            # Sometimes the abstract might be inside a <p> tag within the section
            abstract_parts = response.css('section.item.abstract p ::text').getall()
            abstract = ' '.join(part.strip() for part in abstract_parts if part.strip()).strip()

        item['abstract'] = abstract if abstract else None # Store None if abstract is still empty

        self.logger.info(f"Extracted abstract for: {item['paper_title']}")
        yield item