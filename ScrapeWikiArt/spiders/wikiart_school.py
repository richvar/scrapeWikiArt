import scrapy

from bs4 import BeautifulSoup

from ScrapeWikiArt.items import SchoolItem


class WikiArtArtistSpider(scrapy.Spider):
    name = "wikiart_school"
    allowed_domains = ["wikiart.org"]
    start_urls = ["https://www.wikiart.org/en/artists-by-painting-school"]
    id = 0

    def parse(self, response):
        for style_url in response.xpath('//ul[@class="dictionaries-list"]/li[@class="dottedItem"]/a/@href').getall():
            yield response.follow(style_url, callback=self.parse_style)

    def parse_style(self, response):
        name = response.xpath('//div[@class="dictionary-illustration-container"]//h1/text()').get()
        if not name:
            name = response.xpath('//main/header/h1/text()').get()

        name = name.strip()
        link = response.url

        description_raw = response.xpath('//p[@class="dictionary-description-text"]').get()
        description = BeautifulSoup(description_raw, features="lxml").get_text() if description_raw else description_raw

        yield SchoolItem({
            "Id": self.id,
            "Name": name,
            "Link": link,
            "Description": description,
        })

        self.id += 1

