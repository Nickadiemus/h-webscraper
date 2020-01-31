from classes.requester import requester
from os import environ
import json
import sys

URL='https://www.zillow.com/homes/'

def main():

    searchEntity = requester("austin", "tx", URL)
    searchEntity.search()
    res = searchEntity.content
    print(res.content)



if __name__ == "__main__":
    cont = True
    while(cont):
        city = input("What city would you like to scrape?: ")
        state = input("What state is this city in?: ")

        # todo: add verifiation for city & state input
        

    main()