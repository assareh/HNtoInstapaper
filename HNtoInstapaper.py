import instapaperlib
import string
import twitter
import urllib, urllib2, urlparse, httplib

CONSUMER_KEY = '***'
CONSUMER_SECRET = '***'
ACCESS_TOKEN_KEY = '***'
ACCESS_TOKEN_SECRET = '***'

INSTAPAPER_UN = '***'
INSTAPAPER_PW = '***'

HN_TWITTER = 'newsyc100'
TARGET_URLS = ['newyorker.com','theatlantic.com']

T_CO_SEARCH_KEY = 'https://t.co'

class URLExpander: #https://taoofmac.com/space/blog/2009/08/10/2205
  # known shortening services
  shorteners = ['tr.im','is.gd','tinyurl.com','bit.ly','snipurl.com','cli.gs',
                'feedproxy.google.com','feeds.arstechnica.com']
  twofers = [u'\u272Adf.ws']
  # learned hosts
  learned = []
    
  def resolve(self, url, components):
    """ Try to resolve a single URL """
    c = httplib.HTTPConnection(components.netloc)
    c.request("GET", components.path)
    r = c.getresponse()
    l = r.getheader('Location')
    if l == None:
      return url # it might be impossible to resolve, so best leave it as is
    else:
      return l
  
  def query(self, url, recurse = True):
    """ Resolve a URL """
    components = urlparse.urlparse(url)
    # Check weird shortening services first
    if (components.netloc in self.twofers) and recurse:
      return self.query(self.resolve(url, components), False)
    # Check known shortening services first
    if components.netloc in self.shorteners:
      return self.resolve(url, components)
    # If we haven't seen this host before, ping it, just in case
    if components.netloc not in self.learned:
      ping = self.resolve(url, components)
      if ping != url:
        self.shorteners.append(components.netloc)
        self.learned.append(components.netloc)
        return ping
    # The original URL was OK
    return url

# Authenticate with Twitter API 
api = twitter.Api(consumer_key=CONSUMER_KEY,
                  consumer_secret=CONSUMER_SECRET,
                  access_token_key=ACCESS_TOKEN_KEY,
                  access_token_secret=ACCESS_TOKEN_SECRET)
 
# GetUserTimeline(self, user_id=None, screen_name=None, since_id=None, max_id=None, 
#                 count=None, include_rts=True, trim_user=None, exclude_replies=None)
statuses = api.GetUserTimeline(screen_name=HN_TWITTER, count=200)

# Instapaper Library
from instapaperlib import Instapaper
i = Instapaper(INSTAPAPER_UN, INSTAPAPER_PW)
# print i.auth()
# (statuscode, statusmessage) = i.add_item("URL", "title")

expander = URLExpander() # initialize an expander instance

# Pulls out the link URL from the tweet (link is first URL), and expands from t.co shortlink
def getUrls(statuses):
    urls = []
    for s in statuses:
        if string.find(s.text, 'https://') > -1: # if it contains an https url
            url = s.text[string.find(s.text, 'https://'):string.find(s.text, ' ', string.find(s.text, 'https://'))] # pull out the url
            url_to_add = expander.query(url=url) 
            if string.find(url_to_add, T_CO_SEARCH_KEY) == -1:
                urls.append(url_to_add)
            else: # sometimes urls need expanding more than once
                url_to_add = expander.query(url=url)
                if string.find(url_to_add, T_CO_SEARCH_KEY) == -1:
                    urls.append(url_to_add)
                else:
                    urls.append(expander.query(url_to_add))
            urls.append(expander.query(expander.query(url=url)))
    return urls

# Searches and filters list of URLs for target URL
def filterUrls(urls):
    filtered_urls = []
    for url in urls:
        for targetUrl in TARGET_URLS:
            if string.find(url, targetUrl) > -1: # found
                filtered_urls.append(url)
    return filtered_urls

urls = getUrls(statuses) # extract article URLs from tweets
urls = filterUrls(urls) # filter for articles from the desired website

# Add any results to Instapaper
for url in urls:
    print "added to Instapaper:",url
    i.add_item(url, '')
