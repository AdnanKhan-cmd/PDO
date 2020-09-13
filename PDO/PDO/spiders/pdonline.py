import scrapy
import requests
import sys
import pandas as pd
from scrapy.http import FormRequest
from scrapy.utils.response import open_in_browser

if sys.version_info[0] < 3: 
    from StringIO import StringIO
else:
    from io import StringIO


class PdonlineSpider(scrapy.Spider):
    name = 'pdonline'
    # allowed_domains = ['pdonline.brisbane.gld.gov.au']
    # start_urls = ['http://pdonline.brisbane.gld.gov.au/']

    def start_requests(self):

        self.pause_scraping = False
        """
        input_data = list()
        google_sheet_id =  "1ItXlYbNKUh9buALC-3WObEFJIrXILlCiRBIUJHvX3AA"
        response = requests.get('https://docs.google.com/spreadsheet/ccc?key=' + google_sheet_id + '&output=csv')
        if not response.status_code == 200:
            print("Wrong status code")
            sys.exit(1)
        df = pd.read_csv(StringIO(response.text), sep=",")
        for index, row in df.iterrows():
            input_data.append(row.to_dict())
        """

        urls = list()
        urls = 'https://pdonline.brisbane.qld.gov.au/MasterPlan/Modules/Enquirer/PropertySearch.aspx'

        
        if True: # input_data
            yield scrapy.Request(url=urls, callback=self.search_result, meta={"Cookie_trick" : list(),  "input_data": list()})
            # yield scrapy.Request(url=urls, callback=self.search_result, meta={"Cookie_trick" : list(),  "input_data": input_data.pop()})

    def search_result(self, response):
        if "Default.aspx" in response.url:
            self.pause_scraping = True
            cookie_header = (response.request.headers.get('Cookie')) # Cookie utf-8 to string
            if not cookie_header:
                return []
            cookie_gen_bytes = (s.strip() for s in cookie_header.split(b";"))
            cookie_list_unicode = []
            for cookie_bytes in cookie_gen_bytes:
                try:
                    cookie_unicode = cookie_bytes.decode("utf8")
                except UnicodeDecodeError:
                    logger.warning("Non UTF-8 encoded cookie found in request %s: %s",
                                   request, cookie_bytes)
                    cookie_unicode = cookie_bytes.decode("latin1", errors="replace")
                cookie_list_unicode.append(cookie_unicode)
                dynamic_cookie[ cookie_unicode.split("=")[0] ] = cookie_unicode.split("=")[1]

            form_data = dict()
    
    def submit_form(self, response):
        self.pause_scraping = False
        var_temp = 1