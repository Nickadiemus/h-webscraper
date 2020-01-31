import requests

class requester():
    
    def __init__(self, city, state, url):
        self.city = city
        self.state = state
        self.url = url
        self.content = None

    ########################################################################
    # def formatSearch
    # @params: String
    # @desciption: formats the string to abide by zillows requests
    ########################################################################
    def formatSearch(self, _city, _state):
        return (str(_city).capitalize()+"-"+_state.upper()+"_rb")

    ########################################################################
    # def search
    # @params: self
    # @desciption: searches for the criteria provided
    ########################################################################
    def search(self):
        headers=self.createHeaders()
        post={}
        search = self.formatSearch(self.city, self.state)
        content = requests.get(self.url + search, headers=headers, data=post)
        
        self.content=content

    ########################################################################
    # def createHeaders
    # @params: NA
    # @desciption: creates the required headers
    ########################################################################
    def createHeaders(self):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }
        return headers