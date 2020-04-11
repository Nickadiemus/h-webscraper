import requests
import json
import sys
from bs4 import BeautifulSoup as bs
import ssl
import re
import codecs  #delete for prod

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

BASEURL = "https://www.zillow.com"
PAGE_SUFFIX = "_p"


def createHeaders():
    headers = {
        'accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/4.0'
    }
    return headers


def findBatchRange(page):
    pageRange = 0
    # convert tag to str class
    page = str(page)
    # find all digits inside string
    regex = re.compile('\d+')
    pages = regex.findall(page)

    #find max number in range of indexes found
    for number in pages:
        if pageRange < int(number):
            pageRange = int(number)

    return pageRange


def formatUri(areaCode):
    # Todo: change this to an environment var later on
    # hard coded for now
    return BASEURL + "/homes/" + str(areaCode) + "_rb/"


def formatPageUri(page, base):
    return BASEURL + base + str(page) + PAGE_SUFFIX


def formatBatchUri(length, baseUri):
    urls = []
    # loop through max amount of pages and generate urls for multiprocessing
    for page in range(0, length):
        batchedURL = formatPageUri(page + 1, baseUri)
        urls.append(batchedURL)
    return urls


def makeGetRequest(areaCode):
    headers = createHeaders()
    post = {}
    searchUri = formatUri(areaCode)
    resp = requests.get(searchUri, headers=headers, data=post)
    if resp.ok:
        return resp.content
    return -1


def handler(event, context):
    isDev = True
    pages = []
    pageRange = -1
    batchSuffix = ""
    html = None
    # check if trigger payload is not empty
    if len(event) == 0:
        # log error to cloudwatch
        err = {
            "message": "ERROR: payload with key \"areaCode\" was not provided",
            "input": event
        }
        response = {"statusCode": 403, "body": json.dumps(err)}
        return response

    if not isDev:
        resp = makeGetRequest(event['areaCode'])
        html = bs(resp, 'html.parser')
    else:
        f = codecs.open("tmp/Austin.html", 'r', 'utf-8')
        fileRead = f.read()
        html = bs(fileRead, 'html.parser')
    pagination = html.find_all("a",
                               attrs={
                                   "aria-hidden": "true",
                                   "title": "Previous page"
                               })

    batchSuffix = pagination[0]['href']
    curPage = html.find_all("li", attrs={"aria-current": "page"})

    print("pagination:", pagination)
    print("curPage:", curPage)
    print("PageRange:", pageRange)
    if len(curPage) == 0:
        pageRange = 0
    elif len(curPage) > 1:
        pageRange = -1
        print("found length more than 1")
    else:
        pageRange = findBatchRange(curPage[0].span.contents)

    # check if pageRange is not 0
    # else assume that there is no pagination
    # and send process to worker
    if pageRange == -1:
        return
    elif pageRange == 0:
        page = formatUri(event['areaCode'])
        pages.append(page)
    else:
        pages = formatBatchUri(pageRange, batchSuffix)

    print(pages)
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
    context = {}
    for e in event:
        handler(e, context)