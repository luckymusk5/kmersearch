import scrapy
start_urls=["https://glotelho.cm/products-sitemap.xml"]
class GlotelhoScrape(scrapy.Spider):
    name = "glotelho"
    def start_requests(self):
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        urls = response.xpath("//url/loc/text()").getall()
        product_urls = [url for url in urls if "/products/" in url]
        for product_url in product_urls:
            yield scrapy.Request(url=product_url, callback=self.parse_product)

    def parse_product(self, response):
        title = response.xpath("//meta[@property='og:title']/@content").get()
        price = response.xpath("//span[@class='xl:text-[27px] text-sm xs:text-[1.8rem] lg:text-[28px] lg:leading-normal md:text-[28px] font-bold text-gray-900 font-montserrat font-extrabold']/text()").get()
        description = response.xpath("//meta[@name='description']/@content").get()
        description = ' '.join([desc.strip() for desc in description if desc.strip()])
        images = response.xpath("//meta[@property='og:image']/@content").getall()

        yield {
            'title': title,
            'price': price,
            'description': description,
            'images': images,
            'url': response.url
        }