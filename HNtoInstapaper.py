#!/usr/bin/env python

""" This script finds top articles on Hacker News from sites you specify
    and automatically saves them to Instapaper for later reading """

import os
import sys
import time
import string
import urlparse
from instapaperlib import Instapaper
import requests
import twitter
import hvac


class URLExpander(object):
    """ Class for expanding link shortened URLs
    derived from https://taoofmac.com/space/blog/2009/08/10/2205 """
    # known shortening services
    shorteners = ['t.co', 'tr.im', 'is.gd', 'tinyurl.com', 'bit.ly', 'snipurl.com', 'cli.gs',
                  'feedproxy.google.com', 'feeds.arstechnica.com']
    learned = []

    def resolve(self, url, components):
        """ Try to resolve a single URL """
        response = requests.head(url)
        if response.status_code != 404: # avoid a url not found
            location = response.headers['Location']
            if location is None:
                return url # it might be impossible to resolve, so best leave it as is
            if urlparse.urlparse(location).netloc in self.shorteners:
                return self.resolve(location, components) # multiple shorteners, repeat
            else:
                return location
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


def get_urls(statuses):
    """ Pulls out the link URL from the tweet (link is first URL), and expands from t.co
    shortlink """
    urls = []
    for status in statuses:
        if string.find(status.text, 'https://') > -1: # if it contains an https url
            url = status.text[string.find(status.text, 'https://'):string.find(status.text, ' ',\
                         string.find(status.text, 'https://'))] # pull out the url
            urls.append(EXPANDER.query(url=url))
        # provide a status readout
        sys.stdout.write('.')
        sys.stdout.flush()
    return urls

def filter_urls(urls):
    """ Searches and filters list of URLs for target URL """
    filtered_urls = []
    for url in urls:
        for target_url in TARGET_URLS:
            if string.find(url, target_url) > -1: # found
                filtered_urls.append(url)
    return filtered_urls


# Authenticate to Vault
VAULT_CLIENT = hvac.Client(
    url=os.environ['VAULT_ADDR'],
    token=os.environ['VAULT_TOKEN']
)

# Read the data written under path: hntoinstapaper/instapaper
VAULT_READ_RESPONSE = VAULT_CLIENT.secrets.kv.v2.read_secret_version(mount_point='hntoinstapaper', path='instapaper')

# Write the secrets to variables
INSTAPAPER_UN = VAULT_READ_RESPONSE['data']['data']['username']
INSTAPAPER_PW = VAULT_READ_RESPONSE['data']['data']['password']

# Read the data written under path: hntoinstapaper/twitter
VAULT_READ_RESPONSE = VAULT_CLIENT.secrets.kv.v2.read_secret_version(mount_point='hntoinstapaper', path='twitter')

# Write the secrets to variables
CONSUMER_KEY = VAULT_READ_RESPONSE['data']['data']['CONSUMER_KEY']
CONSUMER_SECRET = VAULT_READ_RESPONSE['data']['data']['CONSUMER_SECRET']
ACCESS_TOKEN_KEY = VAULT_READ_RESPONSE['data']['data']['ACCESS_TOKEN_KEY']
ACCESS_TOKEN_SECRET = VAULT_READ_RESPONSE['data']['data']['ACCESS_TOKEN_SECRET']

# Variable definitions
# be sure to include the target site's standard domain name and link shortened domain name
HN_TWITTER = 'newsyc100'
TARGET_URLS = ['newyorker.com', 'nyer.cm']

# this is so when automated with launchd, the system has time to establish WiFi connection
time.sleep(10)

# Authenticate with Twitter API
API = twitter.Api(consumer_key=CONSUMER_KEY,
                  consumer_secret=CONSUMER_SECRET,
                  access_token_key=ACCESS_TOKEN_KEY,
                  access_token_secret=ACCESS_TOKEN_SECRET)

# Read latest tweet ID scanned from log
F = open(os.path.join(os.path.dirname(__file__), HN_TWITTER) + '.txt', 'a+')
# the above will create the file if it does not exist
F.close()
F = open(os.path.join(os.path.dirname(__file__), HN_TWITTER) + '.txt', 'r+')
LAST_ID = F.readline()

# GetUserTimeline(self, user_id=None, screen_name=None, since_id=None, max_id=None,
#                 count=None, include_rts=True, trim_user=None, exclude_replies=None)
STATUSES = API.GetUserTimeline(screen_name=HN_TWITTER, since_id=LAST_ID, count=200)

if len(STATUSES) > 0:
    # Instapaper Library
    i = Instapaper(INSTAPAPER_UN, INSTAPAPER_PW)

    EXPANDER = URLExpander()

    URLS = get_urls(STATUSES)
    URLS = filter_urls(URLS)

    print ''

    for url in URLS:
        print "added to Instapaper:", url
        i.add_item(url, '')

    print 'Done!'

    # Log latest tweet
    F.seek(0, 0)
    F.write(str(STATUSES[0].id))

else:
    print "No new tweets since this script was last run."

F.close()
