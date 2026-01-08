import scrapy
import re


class GlotelhoScrape(scrapy.Spider):
    name = "glotelho"
    allowed_domains = ["glotelho.cm"]
    start_urls = ["https://glotelho.cm/products-sitemap.xml"]

    custom_settings = {
        "ROBOTSTXT_OBEY": False,

        # Concurrence élevée (raisonnable)
        "CONCURRENT_REQUESTS": 32,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 32,
        "DOWNLOAD_DELAY": 0,

        # Pipeline JSON
        "ITEM_PIPELINES": {
            "glotelhoscrape.pipelines.JsonWriterPipeline": 300,
        },

        # Optimisations
        "COOKIES_ENABLED": False,
        "RETRY_ENABLED": True,
        "LOG_LEVEL": "INFO",
    }

    def parse(self, response):
        product_urls = response.xpath(
            "//*[local-name()='loc' and contains(text(), '/product/')]/text()"
        ).getall()

        self.logger.info(f"Nombre d'URLs produits trouvées : {len(product_urls)}")

        for url in product_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_product,
                dont_filter=True
            )

    def clean_price(self, price_text):
        if not price_text:
            return None

        numbers = re.sub(r"[^\d]", "", price_text)
        return float(numbers) if numbers else None

    def parse_product(self, response):
        title = response.xpath(
            "//meta[@property='og:title']/@content"
        ).get()

        price_raw = response.xpath(
            "//span[contains(@class,'font-bold')]/text()"
        ).get()

        description = response.xpath(
            "//meta[@name='description']/@content"
        ).get()

        images = response.xpath(
            "//meta[@property='og:image']/@content"
        ).getall()

        yield {
            "url": response.url,
            "title": title if title else "none",
            "price": self.clean_price(price_raw),
            "description": description.strip() if description else "none",
            "images": images if images else [],
        }
