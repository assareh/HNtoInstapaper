#!/usr/bin/env python

""" This script finds top articles on Hacker News from sites you specify
    and automatically saves them to Instapaper for later reading """

import os
import sys
import time
import string
import urlparse
import requests
from instapaperlib import Instapaper
import twitter

CONSUMER_KEY = '***'
CONSUMER_SECRET = '***'
ACCESS_TOKEN_KEY = '***'
ACCESS_TOKEN_SECRET = '***'

INSTAPAPER_UN = '***'
INSTAPAPER_PW = '***'

HN_TWITTER = 'newsyc100'
TARGET_URLS = ['newyorker.com', 'nyer.cm', 'theatlantic.com', 'theatln.tc']
# be sure to include the target site's standard domain name and link shortened domain name

class URLExpander(object):
    """ Class for expanding link shortened URLs
    derived from https://taoofmac.com/space/blog/2009/08/10/2205 """
    # known shortening services
    shorteners = ['t.co', 'tr.im', 'is.gd', 'tinyurl.com', 'bit.ly', 'snipurl.com', 'cli.gs',
                  'feedproxy.google.com', 'feeds.arstechnica.com']
    learned = []

    def resolve(self, url, components):
        """ Try to resolve a single URL """
        r = requests.head(url)
        if r.status_code != 404: # avoid a url not found
            l = r.headers['Location']
            if l is None:
                return url # it might be impossible to resolve, so best leave it as is
            if urlparse.urlparse(l).netloc in self.shorteners:
                return self.resolve(l, components) # multiple shorteners, repeat
            else:
                return l
        else:
            return '' # invalid url

    def query(self, url):
        """ Resolve a URL """
        components = urlparse.urlparse(url)
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

# this is so when automated with launchd, the system has time to establish WiFi connection
time.sleep(10)

# Authenticate with Twitter API
api = twitter.Api(consumer_key=CONSUMER_KEY,
                  consumer_secret=CONSUMER_SECRET,
                  access_token_key=ACCESS_TOKEN_KEY,
                  access_token_secret=ACCESS_TOKEN_SECRET)

def getUrls(statuses):
    """ Pulls out the link URL from the tweet (link is first URL), and expands from t.co
    shortlink """
    urls = []
    for s in statuses:
        if string.find(s.text, 'https://') > -1: # if it contains an https url
            url = s.text[string.find(s.text, 'https://'):string.find(s.text, ' ',\
                         string.find(s.text, 'https://'))] # pull out the url
            urls.append(expander.query(url=url))
        # provide a status readout
        sys.stdout.write('.')
        sys.stdout.flush()
    return urls

def filterUrls(urls):
    """ Searches and filters list of URLs for target URL """
    filtered_urls = []
    for url in urls:
        for targetUrl in TARGET_URLS:
            if string.find(url, targetUrl) > -1: # found
                filtered_urls.append(url)
    return filtered_urls

# Read latest tweet ID scanned from log
f = open(os.path.join(os.path.dirname(__file__), HN_TWITTER) + '.txt', 'a+')
# the above will create the file if it does not exist
f.close()
f = open(os.path.join(os.path.dirname(__file__), HN_TWITTER) + '.txt', 'r+')
last_id = f.readline()

# GetUserTimeline(self, user_id=None, screen_name=None, since_id=None, max_id=None,
#                 count=None, include_rts=True, trim_user=None, exclude_replies=None)
statuses = api.GetUserTimeline(screen_name=HN_TWITTER, since_id=last_id, count=200)

if len(statuses) > 0:
    # Instapaper Library
    i = Instapaper(INSTAPAPER_UN, INSTAPAPER_PW)

    expander = URLExpander()

    urls = getUrls(statuses)
    urls = filterUrls(urls)

    print ''

    for url in urls:
        print "added to Instapaper:", url
        i.add_item(url, '')

    print 'Done!'

    # Log latest tweet
    f.seek(0, 0)
    f.write(str(statuses[0].id))

else:
    print "No new tweets since this script was last run."

f.close()
