from botocore.vendored import requests

import json
import sys

def createHeaders():
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
    }

    return headers

def formatUri(areaCode):
    # Todo: change this to an environment var later on
    # hard coded for now
    return "https://www.zillow.com/homes/" +str(areaCode) + "_rb"

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
        
    print(makeGetRequest(event['areaCode']))

    # make initial reqest to determine how many requests will need to be used 

    
    
    
    
    
    
    
    
    
    
    
    
    body = {"message": "Go Serverless v1.0! Your function executed successfully!","input": event}
    response = {"statusCode": 200,"body": json.dumps(body)}
    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration

