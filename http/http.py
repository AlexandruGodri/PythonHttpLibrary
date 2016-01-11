import urllib, urllib2, cookielib, time

from http_method import HTTP_METHOD
from http_user_agent import HTTP_USER_AGENT

'''
Class which allows the user to perform HTTP requests.
You can run chained requests saving cookies across calls.
After each request you get an answer which contains:
    url String - The url which the request finished as (after the eventually redirects, or session id added to the url)
    code Number - The HTTP Status Code returned (200, 404 etc)
    headers Object - Key/Value representation with the response headers
    body String - The response body
    cookies List - List of object with the cookies

Each cookie in the list contains an object like this:
Cookie(version=0, name='JSESSIONID', value='0DBFC411353EDF2E5406E01110E09E62.TCpfix242a', port=None, port_specified=False, domain='example.com', domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=None, discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)

TODO:
- create a DEBUG mode which should be activated on demand and output various data
- create response handlers for json or xml formats
- enable basic http authentication
'''
class HTTP(HTTP_METHOD, HTTP_USER_AGENT):
    ALLOWED_KEYS = "url,headers,method,data,body".split(",")

    '''
    Accepted parameters:
        url - String - The url to call
        headers - Object - Key-Value object with the headers to send with the request
        method - String - The Http method to simulate
        data - Object - Key-Value object with the data to send to the request
        body - String - The request body
    Generally on POST or PUT requests you will provide the "data" field.
    If not provided the data will be taken as an empty list {}.
    "headers" can be something like { "Content-Type": "application/json" }

    Cookies returned after each request is a list with elements like the following:
    Cookie(version=0, name='JSESSIONID', value='0DBFC411353EDF2E5406E01110E09E62.TCpfix242a', port=None, port_specified=False, domain='example.com', domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=None, discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)
    '''
    def __init__(self, **args):
        # init all keys with None
        for key in self.ALLOWED_KEYS:
            setattr(self, key, None)

        # set values received in constructor (url, method etc)
        self.setData(**args)

        # reset (or initialize if the first time) the cookie jar
        self.reset()

    '''
    Loops through the received parameters and saves them only if they are allowed.
    After that, if certain values were not provided, such as the headers, then they are reseted to a default value.
    Default values:
        "headers": {}
        "data": {}
        "method": "GET"
    '''
    def setData(self, **args):
        for key in args:
            if key in self.ALLOWED_KEYS:
                setattr(self, key, args[key])

        if self.headers is None: self.headers = {}
        if self.data is None: self.data = {}
        if self.method is None: self.method = "GET"

    '''
    Resets the cookie jar for usage.
    The method is first called in the constructor.
    It can subsequently be called by the user anytime in the process.
    '''
    def reset(self):
        self.cookieJar = cookielib.LWPCookieJar()
        self.requestHandler = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookieJar))
        urllib2.install_opener(self.requestHandler)

    '''
    Sets the user agent for a request.
    This will be remembered througout the later requests unless changed.
    This can also be passed through the "headers" option in the constructor.
    There is a range of default user agents in the HTTP_USER_AGENT class.
    '''
    def setUserAgent(self, userAgent):
        self.headers["User-agent"] = userAgent

    '''
    Internal Method which actually makes the request
    '''
    def _run(self):
        time_start = time.time()

        try:
            # initialize the request object with the url, data and headers
            if self.body is not None:
                requestBody = self.body
            else:
                requestBody = urllib.urlencode(self.data)
            request = urllib2.Request(self.url, requestBody, self.headers)

            # set the request method
            request.get_method = lambda: self.method

            # set the cookie jar
            self.cookieJar.add_cookie_header(request)

            # perform the request
            response = urllib2.urlopen(request)

            time_end = time.time()

            # get the headers as an key/value representation
            dataHeaders = {}
            for key in response.info():
                dataHeaders[key] = response.info()[key]

            # get the cookies from the response
            dataCookies = {}
            for key, value in enumerate(self.cookieJar):
                dataCookies[key] = value

            # object returned by the function
            data = {
                "url": response.geturl(),
                "code": response.code,
                "headers": dataHeaders,
                "body": response.read(),
                "cookies": dataCookies,
                "duration": time_end - time_start
            }

            return data
        except urllib2.HTTPError as e:
            data = {
                "error": True,
                "exception": e,
                "duration": time.time() - time_start
            }

            if hasattr(e, "code"):
                data["code"] = e.code
            else:
                data["code"] = "NULL"

            return data
        except Exception as e:
            data = {
                "error": True,
                "exception": e,
                "duration": time.time() - time_start
            }

            if "code" in e:
                data["code"] = e.code
            else:
                data["code"] = "NULL"

            return data

    '''
    Method which performs a request and returns the details about the response
    '''
    def run(self, **args):
        self.setData(**args)
        return self._run()
