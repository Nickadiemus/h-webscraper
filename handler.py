# from botocore.vendored import requests
import requests
from datetime import datetime
from bs4 import BeautifulSoup as bs
import json
import sys
import codecs
import re
import ssl
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def createHeaders():
    headers = {
        'accept':
        'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0'
    }
    return headers


def makeGetRequest(url):
    headers = createHeaders()
    post = {}
    resp = requests.get(url, headers=headers, data=post)
    if resp.ok:
        return resp.content
    # log erro
    return None


def filterAttributes(line):
    regex = re.compile(r'\d+|ba|bds|sqft|bd')
    result = regex.findall(line)
    return result


def compareSqft(inp1, inp2):
    inp1 = inp1.replace(',', '')
    return int(inp1) == int(inp2)


def consolidate(jinput, hinput):
    consolidatedData = jinput
    for key in hinput:
        if key == "price":
            consolidatedData[key] = hinput[key]
        elif key == "bds" or key == "bd":
            consolidatedData['bds'] = hinput[key]
        elif key == "ba":
            consolidatedData[key] = hinput[key]
        elif key == "sqft":
            if compareSqft(consolidatedData['floorSize'], hinput['sqft']):
                consolidatedData['floorSize'] = hinput[key]
            else:
                #log to cloudwatch
                print(
                    "[ERROR]: sqft numbers did not match. continuing with json value of sqft"
                )
        else:
            consolidatedData[key] = hinput[key]

    return consolidatedData


def scrapeHtmlData(listing):
    attrs = {}
    listing = str(listing)
    listingHtml = bs(listing, 'html.parser')
    listPrice = listingHtml.find("div", attrs={"class": "list-card-price"})
    try:
        attrs['price'] = listPrice.text
    except:
        print("[ERROR]: could not find value from listPrice.text")

    listHouseDetails = listingHtml.find("ul",
                                        attrs={"class": "list-card-details"})

    try:
        for child in listHouseDetails.children:
            # print(type(child), "|", (str(child).strip()))
            fa = filterAttributes(str(child))
            if len(fa) != 0:
                if len(fa) == 2:
                    attrs[fa[1]] = fa[0]
                else:
                    joinNumber = ''
                    joinNumber = joinNumber.join(fa[:(len(fa) - 1)]).strip()
                    print(joinNumber)
                    attrs[fa[len(fa) - 1]] = joinNumber
    except:
        print("[ERROR]: could not find value from listHouseDetails.children")

    if len(attrs) == 0:
        return None

    return attrs


def scrapeJsonData(listing):

    striped = str(listing).strip()
    listingHtml = bs(striped, 'html.parser')
    jsonListing = listingHtml.find("script")
    #check if script exists
    if jsonListing == None:
        #continue
        return
    try:
        nJson = str(jsonListing.contents[0])
        nJson = json.loads(nJson)
        data = {}
        for i in nJson:
            if i == "@type":
                try:
                    data['house_type'] = nJson[i].strip()
                except:
                    # log error
                    print("[ERROR]: could no add key value ", i)
            elif i == "name":
                try:
                    data['full_address'] = nJson[i].strip()
                except:
                    print("[ERROR]: could no add key value ", i)
            elif i == "floorSize":
                try:
                    data[i] = nJson[i]['value'].strip()
                except:
                    print("[ERROR]: could no add key value ", i)
            elif i == "address":
                try:
                    data['street'] = nJson[i]['streetAddress'].strip()
                    data['city'] = nJson[i]['addressLocality'].strip()
                    data['state'] = nJson[i]['addressRegion'].strip()
                    data['postal_code'] = nJson[i]['postalCode'].strip()
                except:
                    print("[ERROR]: could no add key value ", i)
            elif i == "geo":
                try:
                    data['latitude'] = nJson[i]['latitude']
                    data['longitude'] = nJson[i]['longitude']
                except:
                    print("[ERROR]: could no add key value ", i)
            elif i == "url":
                try:
                    data['url'] = nJson[i].strip()
                except:
                    print("[ERROR]: could no add key value ", i)
            else:
                continue
    except:
        #log json parsing issue to cloudwatch
        print("Error:", "error parsing")

    return data


def handler(event, context):

    listingData = {}
    listingData['listings'] = []
    ts = datetime.now().isoformat()
    listingData['timestamp'] = ts
    isDev = False
    html = None

    # check if trigger payload is not empty
    if len(event['url']) == 0:

        # log error to cloudwatch
        err = {
            "message": "ERROR: payload with key \"areaCode\" was not provided",
            "input": event
        }
        response = {"statusCode": 403, "body": json.dumps(err)}
        return response

    if not isDev:
        houseListings = makeGetRequest(event['url'])
        html = bs(houseListings, 'html.parser')
    else:
        f = codecs.open("tmp/Austin_p1.html", 'r', 'utf-8')
        fileRead = f.read()
        html = bs(fileRead, 'html.parser')

    listings = html.find('ul', attrs={'class': 'photo-cards_short'})
    print(listings)
    listingsChildren = listings.findChildren("li", recursive=False)

    for child in listingsChildren:
        jsonAttrExists = False
        htmlAttrExists = False
        print(
            "____________________________________________________________________________________________________________________________________________________________"
        )
        jsonData = scrapeJsonData(child)
        if jsonData == None:
            continue
        else:
            jsonAttrExists = True
        htmlData = scrapeHtmlData(child)
        if htmlData == None:
            continue
        else:
            htmlAttrExists = True

        if htmlAttrExists and jsonAttrExists:
            consolidatedData = consolidate(jsonData, htmlData)
            if len(consolidatedData) != 0:
                listingData['listings'].append(consolidatedData)
                print(consolidatedData)
        print(
            "____________________________________________________________________________________________________________________________________________________________"
        )

    # make initial reqest to determine how many requests will need to be used

    with open("assets/parsedListings.json", 'w') as outfile:
        json.dump(listingData, outfile)
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }
    response = {"statusCode": 200, "body": json.dumps(body)}
    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration


if __name__ == "__main__":
    event = {"url": "https://www.zillow.com/austin-tx-78745/houses/"}
    context = {}
    handler(event, context)
