import requests
import json
import sys
from bs4 import BeautifulSoup as bs
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def createHeaders():
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0'
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
    
    return resp.content

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
        
    html = makeGetRequest(event['areaCode'])
    parsedHtml = bs(html, 'html.parser')
    parentHouseListing = parsedHtml.find('ul', attrs={'class':'photo-cards_short'})
    childrenHouseListing = parentHouseListing.findChildren("li", recursive=False)
    for listing in childrenHouseListing:
        for item in listing:
            print("item", item)
        return 
    

    # make initial reqest to determine how many requests will need to be used 

if __name__ == "__main__":
    
    event = {
        "areaCode": 40391
    }
    context={}
    handler(event, context)