import scrapy
from scrapy.http import FormRequest
from scrapy.utils.response import open_in_browser
from ast import literal_eval

class CashFlowSpider(scrapy.Spider):
    name = "cashflow"

    url = 'https://www.matrix.nwmls.com/Matrix/Public/Portal.aspx?ID=DE-153870005468&eml=YWRuYW5haG1hZDQ4NzNAZ21haWwuY29t'

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse)

    """ get the overarching page and check every listing inside """
    def parse(self, response):

        open_in_browser(response)

        # go through all the listings
        listing_num = 1
        for listing in response.css('div.multiLineDisplay'):
            listing_link = listing.css('span.d-paddingRight--1')

            # print out the address corresponding to that listing
            print('GOING INSIDE Listing #' + str(listing_num) + ' Address: ' + listing_link.css('a::text').get())
            listing_num = listing_num + 1

            # get the inner page for the listing link
            inner_page = listing_link.css('a::attr(href)').get()
            if inner_page is not None: # make sure it exists

                # process postback information
                inside_paren = inner_page[inner_page.find('(')+1:inner_page.find(')')]
                event_target = inside_paren[0:inside_paren.find(',')]
                event_argument = inside_paren[inside_paren.find(',')+1:len(inside_paren)]

                # print postback arguments
                print('__EVENTTARGET' + event_target)
                print('__EVENTARGUMENT' + event_argument)

                formdata = dict()
                formdata['__EVENTTARGET'] = literal_eval(event_target)
                formdata['__EVENTARGUMENT'] = literal_eval(event_argument)

                yield FormRequest.from_response(
                    response,
                    formdata=formdata,
                    callback=self.parse_inner,
                    dont_click=True)

    """ parses the inner page of each listing to get financial information """
    def parse_inner(self, response):

        open_in_browser(response)


