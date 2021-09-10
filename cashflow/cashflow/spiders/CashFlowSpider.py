import scrapy
from scrapy.http import FormRequest
from cashflow.items import CashflowItem
from ast import literal_eval


class CashFlowSpider(scrapy.Spider):
    name = "cashflow"

    start_urls = [
        "https://www.matrix.nwmls.com/Matrix/Public/Portal.aspx?ID=DE-162767573822&eml=YWRuYW5haG1hZDQ4NzNAZ21haWwuY29t"
    ]

    # def start_requests(self):

    # yield scrapy.Request(url=self.url, callback=self.parse)

    def remove_unnecessary_chars(self, line):
        if line[0] == "$":
            line = line[1:]
        line = line.replace(",", "")
        return line

    """ get the overarching page and check every listing inside """

    def parse(self, response):

        # open_in_browser(response)
        items = []

        # go through all the listings
        listing_num = 1
        for listing in response.css("div.multiLineDisplay"):
            listing_link = listing.css("span.d-paddingRight--1")

            # print out the address corresponding to that listing
            print(
                "GOING INSIDE Listing #"
                + str(listing_num)
                + " Address: "
                + listing_link.css("a::text").get()
            )
            listing_num = listing_num + 1

            # get the inner page for the listing link
            inner_page = listing_link.css("a::attr(href)").get()
            if inner_page is not None:  # make sure it exists

                # process postback information
                inside_paren = inner_page[
                    inner_page.find("(") + 1 : inner_page.find(")")
                ]
                event_target = inside_paren[0 : inside_paren.find(",")]
                event_argument = inside_paren[
                    inside_paren.find(",") + 1 : len(inside_paren)
                ]

                # post postback arguments
                formdata = dict()
                formdata["__EVENTTARGET"] = literal_eval(event_target)
                formdata["__EVENTARGUMENT"] = literal_eval(event_argument)

                yield FormRequest.from_response(
                    response,
                    formdata=formdata,
                    callback=self.parse_inner,
                    dont_click=True,
                )

                # items.append(item)
                # print("ITEMS " + str(item))

    """ parses the inner page of each listing to get financial information """

    def parse_inner(self, response):

        item = CashflowItem()

        # open_in_browser(response)
        result = ""

        # get address information
        address_information = response.css(
            "div.d-mega.d-fontSize--mega.d-color--brandDark.col-sm-12"
        )
        info = address_information.css("span.d-paddingRight--1::text").get()
        # print('Adddress: ' + info)
        item["address"] = info

        # print city
        info = (
            response.css("div.col-sm-12.d-textSoft")
            .css("span.d-paddingRight--1::text")
            .get()
        )
        result += "Location: " + info
        result += "\n"
        # print('City: ' + info)
        item["city"] = info[1:]

        # print listing price and annual insurance expense
        general_description = response.css(
            "div.col-xs-6.inherit.inherit.inherit.J_sect"
        )
        for block in general_description:
            property = block.css("span.d-paddingRight--4.d-text::text").get()
            if property == "Listing Price":
                info = block.css("span.d-textStrong::text").get()
                # print(property + ": " + info)
                result += property + ": " + info
                result += "\n"
                item["listing_price"] = self.remove_unnecessary_chars(info)

        for block in general_description:
            property = block.css("span.d-paddingRight--4.d-text::text").get()
            if property == "Insurance Expenses":
                info = block.css("span.d-textStrong::text").get()
                # print(property + ": " + info)
                result += property + ": " + info
                result += "\n"
                item["insurance_expenses"] = self.remove_unnecessary_chars(info)

        # print style code
        listing_information = response.css("div.col-xs-6.J_sect")
        for block in listing_information:
            property = block.css("span.d-paddingRight--4.d-text::text").get()
            if property == "Style Code":
                info = block.css("span.d-textStrong::text").get()
                # print(property + ": " + info)
                info = "".join(info.split(" ")[2])
                result += property + ": " + info
                result += "\n"
                item["style_code"] = info

        # print annual tax
        listing_information = response.css("div.col-xs-6.J_sect")
        for block in listing_information:
            property = block.css("span.d-paddingRight--4.d-text::text").get()
            if property == "Taxes Annual":
                info = block.css("span.d-textStrong::text").get()
                # print(property + ": " + info)
                result += property + ": " + info
                result += "\n"
                item["taxes_annual"] = self.remove_unnecessary_chars(info)

        # print unit information
        units = response.css("div.multiLineDisplay.ajax_display.d14279m_show")
        num_units = len(units)
        # print('Number of units: ' + str(num_units))

        result += "Number of units: " + str(num_units)
        result += "\n"
        item["num_units"] = str(num_units)

        i = 1
        total_unit_rent = 0
        unit_rents = []
        for unit in units:
            unit_properties = unit.css("div.col-xs-6.inherit.col-md-4.col-lg-3.J_sect")

            for unit_property in unit_properties:

                unit_property_name = unit_property.css(
                    "span.d-text.d-paddingRight--4::text"
                ).get()
                if unit_property_name == "Unit Rent":
                    info = unit_property.css("span.d-textStrong::text").get()
                    # print(unit_property_name + " " + str(i) + ": " + info)

                    result += unit_property_name + " " + str(i) + ": " + info
                    result += "\n"
                    i = i + 1
                    total_unit_rent += int(info)
                    unit_rents.append(int(info))
        item["units"] = unit_rents
        # print("INSIDE " + str(item))
        yield item
        # print(csv_row)
