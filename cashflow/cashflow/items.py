# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class CashflowItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    address = scrapy.Field()
    city = scrapy.Field()
    listing_price = scrapy.Field()
    insurance_expenses = scrapy.Field()
    style_code = scrapy.Field()
    taxes_annual = scrapy.Field()
    num_units = scrapy.Field()
    units = scrapy.Field()
    pass
