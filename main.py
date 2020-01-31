from classes.requester import requester
from os import environ
import json
import sys

URL='https://www.zillow.com/homes/'
GEOGRAPHY_FILE_PATH = environ.get("GEOGRAPHY_FILE")
STATE_ABR_FILE_PATH = environ.get("STATE_ABR_FILE")

########################################################################
# def search
# @params: Array
# @desciption: initializes the proper class for making the request to
# retrieve listings from the city and state
########################################################################
def search(uinput):
    searchEntity = requester(uinput[0], uinput[1], URL)
    searchEntity.search()
    res = searchEntity.content
    print(res.content)

########################################################################
# def abrv
# @params: String
# @desciption: converts the state name to its abbreviation
########################################################################
def abrv(state):
    with open(STATE_ABR_FILE_PATH, 'r') as infile:
        data = json.load(infile)
        for _state in data:
            if _state['name'].lower() == state.lower():
                return _state['abbreviation'].upper()
        return None
 
########################################################################
# def validate
# @params: String, String
# @desciption: validates that the city & state exists so the url can be
# formmated correctly
########################################################################
def validate(city, state):
    try:
        with open(GEOGRAPHY_FILE_PATH, 'r') as infile:
            data = json.load(infile)
            infile.close()
            foundCity = False
            foundState = False
            # check city
            for entry in data:
                if(foundCity and foundState):
                    return True
                if entry['city'].lower() == city.lower():
                    print("Found City E: " + entry['city']) 
                    foundCity = True
                    if entry['state'].lower() == state.lower():
                        print("Found State E: " + entry['state']) 
                        foundState = True
                    else:
                        print("City Did not Match State")

    except FileNotFoundError:
        print(FileNotFoundError)

    return False

########################################################################
# def getInput
# @params: None 
# @desciption: drives the user input and returns and array of the city 
# and state if it is valid
########################################################################
def getInput():
    
    validInput = False
    uinput = []
    while(not(validInput)):
        city = input("What city would you like to scrape?: ")
        state = input("What state is this city in?: ")   
        if(validate(city,state)):
            validInput = True
            uinput.append(city)
            abr = abrv(state)
            if(abr != None):
                uinput.append(abr)
            else:
                print("Error: Something went wrong with the conversion")
                exit
                
        else:
            print("Sorry, we could not find that city/state")
            print("Please try again!")
    
    return uinput

if __name__ == "__main__":
    
    # pass city and state vars
    uinput = getInput()
    search(uinput)