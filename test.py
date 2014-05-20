#our imports
from http.http import HTTP

#load home page
h = HTTP(url = "http://example.com")
h.setUserAgent(HTTP.HTTP_USER_AGENT_FIREFOX_31)
result = h.run()

#load login page
h.setData(url = "http://example.com/login")
result = h.run()

#submit login credentials
loginData = {
    "username": "user",
    "password": "pass"
}
h.setData(url = "http://example.com/dologin", method = HTTP.HTTP_METHOD_POST, data = loginData)
result = h.run()

print result
