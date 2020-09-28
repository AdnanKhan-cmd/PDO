import scrapy
import requests
import sys
import pandas as pd
from scrapy.http import FormRequest
from scrapy.utils.response import open_in_browser
import json
from scrapy_splash import SplashRequest, SplashFormRequest

if sys.version_info[0] < 3: 
    from StringIO import StringIO
else:
    from io import StringIO

script = """
function main(splash)
  splash:init_cookies(splash.args.cookies)
  assert(splash:go{
    splash.args.url,
    headers=splash.args.headers,
    http_method=splash.args.http_method,
    body=splash.args.body,
    })
  assert(splash:wait(0.5))

  local entries = splash:history()
  local last_response = entries[#entries].response
  return {
    url = splash:url(),
    headers = last_response.headers,
    http_status = last_response.status,
    cookies = splash:get_cookies(),
    html = splash:html(),
  }
end
"""

class PdonlineSpider(scrapy.Spider):
    name = 'pdonline'

    def start_requests(self):
        self.dynamic_cookie = {}


        yield SplashRequest(
            url="https://pdonline.brisbane.qld.gov.au/MasterPlan/Modules/Enquirer/PropertySearch.aspx",
            # cookies=self.dynamic_cookie,
            callback=self.search_result,
            endpoint='execute',
            cache_args=['lua_source'],
            args={
                'timeout': '90',
                'wait': '30',
                'lua_source': script,
            },
            session_id='1',
            meta={
                "input_data":{
                    'Lot Number':'', 
                    'Plan Number': '', 
                    'Unit Number To':'', 
                    'Unit Number From':'', 
                    'Street Name': 'Mcconaghy St', 
                    'Street Number From': 92, 
                    'Street Number To': 92, 
                    'Suburb': 'Mitchelton'
                    }, 
                "current_url":"https://pdonline.brisbane.qld.gov.au/MasterPlan/Modules/Enquirer/PropertySearch.aspx"
                }
            )

        # Commented below section is about google sheet reading etc.

        """
        google_sheet_id =  "1ItXlYbNKUh9buALC-3WObEFJIrXILlCiRBIUJHvX3AA" # https://docs.google.com/spreadsheets/d/1ItXlYbNKUh9buALC-3WObEFJIrXILlCiRBIUJHvX3AA/edit?usp=sharing
        try:
            res = requests.get('https://docs.google.com/spreadsheet/ccc?key=' + google_sheet_id + '&output=csv')
        except:
            pass
        if not res.status_code == 200:
            print("Wrong status code")
            sys.exit(1)
        df = pd.read_csv(StringIO(res.text), sep=",")
        for index, row in df.iterrows():
            self.input_data.append(row.to_dict())
        
        self.input_data.pop(0)
        urls = list()
        urls = 'https://pdonline.brisbane.qld.gov.au/MasterPlan/Modules/Enquirer/PropertySearch.aspx'


        if self.input_data: # input_data
            yield scrapy.Request(url=urls, cookies=self.dynamic_cookie, callback=self.search_result, meta={"input_data": self.input_data.pop(), "current_url":urls})
        """
    

    def search_result(self, response):
        if response.css("#ctl00_RadWindow1_C_btnOk"):

            form_data = dict()
            input_fields = response.css("form input")
            for ifield in input_fields:
                if ifield.css("input::attr(name)").extract_first() == None:
                    continue
                if ifield.css("input::attr(value)").extract_first() == None:
                    form_data[ifield.css("input::attr(name)").extract_first()] = ''
                elif ifield.css("input::attr(value)").extract_first() == 'I Disagree':
                    continue
                elif ifield.css("input::attr(value)").extract_first() == '':
                    form_data[ifield.css("input::attr(name)").extract_first()] = ''
                else:
                    form_data[ifield.css("input::attr(name)").extract_first()] = ifield.css("input::attr(value)").extract_first()

            yield SplashFormRequest(
                url='https://pdonline.brisbane.qld.gov.au/MasterPlan/Modules/Enquirer/PropertySearch.aspx', 
                formdata=form_data,
                callback=self.search_result,
                endpoint='execute',
                args={
                    'timeout': '90',
                    'wait': '30',
                    'lua_source': script,
                },
                session_id='1',
                meta={
                    'input_data': response.meta["input_data"],
                }
                )
        else:
            # Cookie handling
            for cookie in response.data["cookies"]:
                self.dynamic_cookie[ cookie["name"] ] = cookie["value"]

            form_data = dict()
            input_fields = response.css("form input")
            for ifield in input_fields:
                if ifield.css("input::attr(name)").extract_first() == None:
                    continue
                if ifield.css("input::attr(value)").extract_first() == None:
                    form_data[ifield.css("input::attr(name)").extract_first()] = ''
                else:
                    form_data[ifield.css("input::attr(name)").extract_first()] = ifield.css("input::attr(value)").extract_first()
            for key in response.meta["input_data"]:
                #  if response.meta["input_data"][key]:
                
                if key == "Suburb":
                    form_data["ctl00$MainContent$SuburbCombo"] = response.meta["input_data"][key]
                elif key == "Street Name":
                    street_name_define = {"logEntries":[],"value":"","text":"","enabled":True,"checkedIndices":[],"checkedItemsTextOverflows":False}
                    street_name_define["value"] = response.meta["input_data"][key]
                    street_name_define["text"] =response.meta["input_data"][key]
                    form_data["ctl00_MainContent_StreetCombo_ClientState"] = street_name_define
                    form_data["ctl00$MainContent$StreetCombo"] = response.meta["input_data"][key]
                elif key == "Unit Number From": 
                    form_data["ctl00$MainContent$FromUnitNumberTextBox"] = response.meta["input_data"][key]
                    ctl00_MainContent_FromUnitNumberTextBox_ClientState = {"enabled":True,"emptyMessage":"","validationText":"","valueAsString":"","lastSetTextBoxValue":""}
                    ctl00_MainContent_FromUnitNumberTextBox_ClientState["validationText"] = response.meta["input_data"][key]
                    ctl00_MainContent_FromUnitNumberTextBox_ClientState["valueAsString"] = response.meta["input_data"][key]
                    ctl00_MainContent_FromUnitNumberTextBox_ClientState["lastSetTextBoxValue"] = response.meta["input_data"][key]
                    form_data["ctl00_MainContent_FromUnitNumberTextBox_ClientState"] = ctl00_MainContent_FromUnitNumberTextBox_ClientState
                elif key == "Unit Number To":
                    form_data["ctl00$MainContent$ToUnitNumberTextBox"] = response.meta["input_data"][key]
                    ctl00_MainContent_ToUnitNumberTextBox_ClientState = {"enabled":True,"emptyMessage":"","validationText":"","valueAsString":"","lastSetTextBoxValue":""}
                    ctl00_MainContent_ToUnitNumberTextBox_ClientState["validationText"] = response.meta["input_data"][key]
                    ctl00_MainContent_ToUnitNumberTextBox_ClientState["valueAsString"] = response.meta["input_data"][key]
                    ctl00_MainContent_ToUnitNumberTextBox_ClientState["lastSetTextBoxValue"] = response.meta["input_data"][key]
                    form_data["ctl00_MainContent_ToUnitNumberTextBox_ClientState"] = ctl00_MainContent_ToUnitNumberTextBox_ClientState
                elif key == "Street Number From":
                    form_data["ctl00$MainContent$FromStreetNumberTextBox"] = response.meta["input_data"][key]
                    ctl00_MainContent_FromStreetNumberTextBox_ClientState = {"enabled":True,"emptyMessage":"","validationText":"","valueAsString":"","lastSetTextBoxValue":""}
                    ctl00_MainContent_FromStreetNumberTextBox_ClientState["validationText"] = response.meta["input_data"][key]
                    ctl00_MainContent_FromStreetNumberTextBox_ClientState["valueAsString"] = response.meta["input_data"][key]
                    ctl00_MainContent_FromStreetNumberTextBox_ClientState["lastSetTextBoxValue"] = response.meta["input_data"][key]
                    form_data["ctl00_MainContent_FromStreetNumberTextBox_ClientState"] = ctl00_MainContent_FromStreetNumberTextBox_ClientState
                elif key == "Street Number To":
                    form_data["ctl00$MainContent$ToStreetNumberTextBox"] = response.meta["input_data"][key]
                    ctl00_MainContent_ToStreetNumberTextBox_ClientState = {"enabled":True,"emptyMessage":"","validationText":"","valueAsString":"","lastSetTextBoxValue":""}
                    ctl00_MainContent_ToStreetNumberTextBox_ClientState["validationText"] = response.meta["input_data"][key]
                    ctl00_MainContent_ToStreetNumberTextBox_ClientState["valueAsString"] = response.meta["input_data"][key]
                    ctl00_MainContent_ToStreetNumberTextBox_ClientState["lastSetTextBoxValue"] = response.meta["input_data"][key]
                    form_data["ctl00_MainContent_ToStreetNumberTextBox_ClientState"] = ctl00_MainContent_ToStreetNumberTextBox_ClientState

                elif key == "Plan Number":
                    form_data["ctl00$MainContent$PlanTextBox"] = response.meta["input_data"][key]
                    ctl00_MainContent_PlanTextBox_ClientState = {"enabled":True,"emptyMessage":"","validationText":"","valueAsString":"","lastSetTextBoxValue":""}
                    ctl00_MainContent_PlanTextBox_ClientState["validationText"] = response.meta["input_data"][key]
                    ctl00_MainContent_PlanTextBox_ClientState["valueAsString"] = response.meta["input_data"][key]
                    ctl00_MainContent_PlanTextBox_ClientState["lastSetTextBoxValue"] = response.meta["input_data"][key]
                elif key == "Lot Number":
                    form_data["ctl00$MainContent$LotTextBox"] = response.meta["input_data"][key]
                    ctl00_MainContent_LotTextBox_ClientState = {"enabled":True,"emptyMessage":"","validationText":"","valueAsString":"","lastSetTextBoxValue":""}
                    ctl00_MainContent_LotTextBox_ClientState["validationText"] = response.meta["input_data"][key]
                    ctl00_MainContent_LotTextBox_ClientState["valueAsString"] = response.meta["input_data"][key]
                    ctl00_MainContent_LotTextBox_ClientState["lastSetTextBoxValue"] = response.meta["input_data"][key]
                    form_data["ctl00_MainContent_LotTextBox_ClientState"] = ctl00_MainContent_LotTextBox_ClientState
                else:
                    pass

            for key in form_data:
                if isinstance(form_data[key], dict):
                    form_data[key] = json.dumps(form_data[key])
                if isinstance(form_data[key], int):
                    form_data[key] = str(form_data[key])

            # first method that i used to submit form
            yield FormRequest(
                url='https://pdonline.brisbane.qld.gov.au/MasterPlan/Modules/Enquirer/PropertySearch.aspx', 
                formdata=form_data,
                callback=self.submit_form,
                cookies=self.dynamic_cookie
                )

            # Second method that i have used to submit form
            yield SplashFormRequest(
            url='https://pdonline.brisbane.qld.gov.au/MasterPlan/Modules/Enquirer/PropertySearch.aspx', 
            formdata=form_data,
            callback=self.submit_form,
            endpoint='execute',
            args={
                'timeout': '90',
                'wait': '30',
                'lua_source': script,
            },
            session_id='1'
            )


    def submit_form(self, response):
        var_temp = 1