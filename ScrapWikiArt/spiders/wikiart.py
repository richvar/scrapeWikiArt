import scrapy
from bs4 import BeautifulSoup


class WikiArtPostImpressionismSpider(scrapy.Spider):
    name = "wikiart_post_impressionism"
    allowed_domains = ["wikiart.org"]
    start_urls = ["https://www.wikiart.org/en/artists-by-art-movement/post-impressionism"]

    custom_settings = {
        "FEEDS": {
            "data/post_impressionism.csv": {"format": "csv", "overwrite": True}
        },
        "ITEM_PIPELINES": {'scrapy.pipelines.images.ImagesPipeline': 1},
        "IMAGES_STORE": "data/img",
    }

    def parse(self, response):
        # Extract artist profile URLs
        artist_urls = response.xpath('//li/a[contains(@href, "/en/")]/@href').getall()
        for url in artist_urls:
            artist_page = response.urljoin(url + "/all-works/text-list")
            yield scrapy.Request(artist_page, callback=self.parse_artist)

    def parse_artist(self, response):
        # Extract painting URLs from artist's "text-list" page
        painting_urls = response.xpath('//ul[@class="painting-list-text"]/li/a/@href').getall()
        for painting_url in painting_urls:
            yield response.follow(painting_url, callback=self.parse_painting)

    def parse_painting(self, response):
        def extract_text(xpath_expr):
            return response.xpath(xpath_expr).get(default="").strip()

        title = extract_text("//h3/text()")
        artist = extract_text("//h5[@itemprop='creator']//a/text()")
        year = extract_text("//li[.//s[contains(text(),'Date:')]]/span[@itemprop='dateCreated']/text()")
        image_url = response.xpath('//img[@itemprop="image"]/@src').get()

        styles = response.xpath("//li[.//s[contains(text(),'Style:')]]/span/a/text()").getall()
        genres = response.xpath("//li[.//s[contains(text(),'Genre:')]]/span/a/span/text()").getall()
        media = response.xpath("//li[.//s[contains(text(),'Media:')]]/span/a/text()").getall()
        dimensions = extract_text("//li[.//s[contains(text(),'Dimensions:')]]/text()")

        # Get description of painting if one exists
        description_html = response.xpath('//div[@id="info-tab-description"]/p').get()
        description = BeautifulSoup(description_html, "lxml").get_text(strip=True) if description_html else ""

        # Only scrape paintings marked as post-impressionism
        if any("post-impressionism" in s.lower() for s in styles):
            yield {
                "Title": title,
                "Artist": artist,
                "Year": year,
                "ImageURL": image_url,
                "Styles": "; ".join(styles),
                "Genres": "; ".join(genres),
                "Media": "; ".join(media),
                "Dimensions": dimensions,
                "Description": description,
                "PaintingURL": response.url,
                "image_urls": [image_url],
            }