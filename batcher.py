import requests
import json
import sys
from bs4 import BeautifulSoup as bs
import ssl
import re
import codecs #delete for prod

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def findBatchLengh(page):
    page = str(page)
    # print(type(page),"|",page) 
    regex = re.compile('\d+')
    print(regex.findall(page))


def createHeaders():
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/4.0'
    }

    return headers

def formatUri(areaCode):
    # Todo: change this to an environment var later on
    # hard coded for now
    return "https://www.zillow.com/homes/" +str(areaCode) + "_rb/"

def makeGetRequest(areaCode):
    headers=createHeaders()
    post={}
    searchUri=formatUri(areaCode)
    resp = requests.get(searchUri, headers=headers, data=post)
    print("Resp:",resp.ok)
    if resp.ok:
        return resp.content
    return -1

def handlerProd(event):
    resp = makeGetRequest(event['areaCode'])
    if resp != -1:
        html = bs(resp, 'html.parser')
        # pagination = html.find_all("nav", attrs={"role":"navigation","aria-label":"Pagination"})
        curPage = html.find_all("li", attrs={"aria-current":"page"})
        print(curPage)
        if len(curPage) == 0:
            print("could only have one page of results")
            return
        elif len(curPage) > 1:
            #loop through array and find the correct list
            print("found length more than 1")
        else:
            findBatchLengh(curPage[0])

def handlerDev():
    f = codecs.open("tmp/Austin.html", 'r')
    htmlFile = f.read()
    html = bs(htmlFile, 'html.parser')
    # pagination = html.find_all("nav", attrs={"role":"navigation","aria-label":"Pagination"})
    curPage = html.find_all("li", attrs={"aria-current":"page"})
    
    if len(curPage) == 0:
        print("could only have one page of results")
        return
    elif len(curPage) > 1:
        #loop through array and find the correct list
        print("found length more than 1")
    else:
        findBatchLengh(curPage[0].span.contents)
    

def handler(event, context):

    # check if trigger payload is not empty
    if len(event) == 0:

        # log error to cloudwatch
        err = {
            "message": "ERROR: payload with key \"areaCode\" was not provided",
            "input": event 
        }
        response = {
            "statusCode": 403,
            "body": json.dumps(err)
        }
        return response
    isDev = True

    urlPagePath=""
    pages = []
    if not isDev:
        handlerProd(event)
    else:
        handlerDev()
    
    # print("error")

    # make initial reqest to determine how many requests will need to be used 



if __name__ == "__main__":
    
    event = [{
        "areaCode": 40391
    }
    # {
    #     "areaCode": 40506
    # },
    # {
    #     "areaCode": 40229
    # }
    ]
    context={}
    for e in event:   
        handler(e, context)