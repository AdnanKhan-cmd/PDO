import scrapy
import requests
import sys
import pandas as pd
from scrapy.http import FormRequest
from scrapy.utils.response import open_in_browser
import json

if sys.version_info[0] < 3: 
    from StringIO import StringIO
else:
    from io import StringIO


def url_genrate(url):
    return "http://localhost:8050/render.html?url=%s&imeout=90&wait=3" % url


class PdonlineSpider(scrapy.Spider):
    name = 'pdonline'
    # allowed_domains = ['pdonline.brisbane.gld.gov.au']
    # start_urls = ['http://pdonline.brisbane.gld.gov.au/']

    def start_requests(self):

        self.pause_scraping = False
        self.dynamic_cookie = dict()
        
        self.input_data = list()
        yield FormRequest(
            # url="http://0.0.0.0:8050",
            url="https://enuoaw1oha7wh2x.m.pipedream.net",
            callback=self.search_result,
            formdata={
                'url': 'https://pdonline.brisbane.qld.gov.au/MasterPlan/Modules/Enquirer/PropertySearch.aspx',
            },
            headers={
                'Content-Type': 'application/json',
                'accept': '/',
                }

        )
        '''
        yield scrapy.Request(
            url=url_genrate("https://pdonline.brisbane.qld.gov.au/MasterPlan/Modules/Enquirer/PropertySearch.aspx"),
            cookies=self.dynamic_cookie,
            callback=self.search_result,
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
        '''
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
                list_temp = cookie_unicode.split("=")
                name = list_temp.pop(0)
                value = "=".join(list_temp)
                self.dynamic_cookie[ name ] = value
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
            # yield FormRequest(url="https://a5e2b30d7f61942f28ea0a18796b4020.m.pipedream.net", cookies=self.dynamic_cookie, formdata=form_data, callback=self.temp, meta={"input_data": response.meta["input_data"], "current_url":response.meta["current_url"]})
            yield FormRequest(url=response.meta["current_url"], cookies=self.dynamic_cookie, formdata=form_data, callback=self.search_result, meta={"input_data": response.meta["input_data"], "current_url":response.meta["current_url"]})
        else:
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
                form_data["ctl00$RadScriptManager1"] = "ctl00$MainContent$ctl00$MainContent$SearchPanelPanel|ctl00$MainContent$btnSearch"
                form_data["ctl00_RadScriptManager1_TSM"] = ";;System.Web.Extensions, Version=3.5.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35:en-US:16997a38-7253-4f67-80d9-0cbcc01b3057:ea597d4b:b25378d2;Telerik.Web.UI, Version=2020.2.617.35, Culture=neutral, PublicKeyToken=121fae78165ba3d4:en-US:652a635d-78ca-4fc5-989f-3396e0ef31ee:16e4e7cd:ed16cbdc:f7645509:88144a7a:24ee1bba:33715776:e330518b:1e771326:8e6f0d33:1f3a7489:4877f69a:b2e06756:92fe8ea0:fa31b949:c128760b:19620875:874f8ea2:f46195d3:490a9d4e:bd8f85e4:2003d0b8:aa288e2d:258f1c72:b7778d6c;"
                form_data["ctl00_MainContent_RadTabStrip1_ClientState"] = {"selectedIndexes":["0"],"logEntries":[],"scrollState":{}}
            
            try:
                form_data.pop("ctl00_RadWindow1_C_CMSSection_EditWindow_ClientState, None")
            except:
                pass
            try:
                form_data.pop("ctl00_RadWindow1_C_CMSSection_RadWindowManager1_ClientState, None")
            except:
                pass
            try:
                form_data.pop("ctl00$RadWindow1$C$btnNo, None")
            except:
                pass

            for key in form_data:
                if isinstance(form_data[key], dict):
                    form_data[key] = json.dumps(form_data[key])
                if not isinstance(form_data[key], str):
                    form_data[key] = str(form_data[key])
            yield FormRequest(url=response.meta["current_url"], formdata=form_data, callback=self.search_result, meta={"input_data": list(), "current_url":response.meta["current_url"]})
            yield FormRequest(url=response.meta["current_url"], formdata=form_data, callback=self.search_result, meta={"input_data": list(), "current_url":response.meta["current_url"]})

    
    def temp(self, response):
        pass


    def submit_form(self, response):
        self.pause_scraping = False
        var_temp = 1