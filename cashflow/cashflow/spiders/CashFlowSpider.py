import scrapy

class CashFlowSpider(scrapy.Spider):
    name = "cashflow"

    start_urls = [
        'https://www.matrix.nwmls.com/Matrix/Public/Portal.aspx?ID=DE-153870005468&eml=YWRuYW5haG1hZDQ4NzNAZ21haWwuY29t'
    ]

    """ get the overarching page and check every listing inside """
    def parse(self, response):

        # go through all the listings
        listing_num = 1
        for listing in response.css('div.multiLineDisplay'):
            listing_link = listing.css('span.d-paddingRight--1')

            # print out the address corresponding to that listing
            print('Listing #' + str(listing_num) + ' Address: ' + listing_link.css('a::text').get())
            listing_num = listing_num + 1

            # get the inner page for the listing link
            inner_page = listing_link.css('a::attr(href)').get()
            if inner_page is not None: # make sure it exists
                yield response.follow(inner_page, callback=self.parse_inner)


    """ parses the inner page of each listing to get financial information """
    def parse_inner(self, response):
        print('test')

