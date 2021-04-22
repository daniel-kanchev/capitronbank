import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from capitronbank.items import Article
import requests
import json


class capitronbankSpider(scrapy.Spider):
    name = 'capitronbank'
    start_urls = [
        'https://www.capitronbank.mn/c/%D0%BC%D1%8D%D0%B4%D1%8D%D1%8D-%D0%BC%D1%8D%D0%B4%D1%8D%D1%8D%D0%BB%D1%8D%D0%BB?lang=&type=']

    def parse(self, response):
        json_response = json.loads(
            requests.get("https://www.capitronbank.mn/admin//wp-json/menus/v1/menus/main-menu").text)
        items = json_response["items"]
        links = []
        for item in items:
            articles = item['child_items']
            for article in articles:
                links.append(article['url'])

        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h2/a/text()').get()  or response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//li[@class="post-date meta-wrapper"]/span/a/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@class="entry-content"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
