import scrapy
from scrapy.crawler import CrawlerProcess
from cashflow.cashflow.spiders.CashFlowSpider import CashFlowSpider
"""
from oauth2client.service_account import ServiceAccountCredentials
import gspread

scope = ['https://www.googleapis.com/auth/spreadsheets',
         'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name(
    'credentials.json', scope)

client = gspread.authorize(creds)

test = client.open('Real Estate Cashflow').sheet1
test.update_cell(1, 1, 'hello world')
"""

# run scrapy cashflow spider
process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})

process.crawl(CashFlowSpider)
result = process.start()

# extract data from csv file
