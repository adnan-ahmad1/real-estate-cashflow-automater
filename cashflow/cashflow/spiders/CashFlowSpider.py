import scrapy

class CashFlowSpider(scrapy.Spider):
    name = "cashflow"

    start_urls = [
        'https://www.matrix.nwmls.com/Matrix/Public/Portal.aspx?ID=DE-153870005468&eml=YWRuYW5haG1hZDQ4NzNAZ21haWwuY29t',
    ]