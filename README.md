# HNtoInstapaper
*Find top articles on [Hacker News](http://news.ycombinator.com) from sites you like and automatically save them to Instapaper to read later.*

The @newsyc100 Twitter account tweets links posted to Hacker News that have earned 100 or more points.

I like reading The New Yorker and The Atlantic, but this script can be used for any websites. This script checks the last 200 tweets from the @newsyc100 Twitter account, looks for links to New Yorker and Atlantic articles, and then sends any results to your Instapaper account.

It will log the unique ID of the most recent scanned tweet so subsequent runs will be much faster.

To use, populate your Twitter API credentials and Instapaper account credentials. Edit the TARGET_URLS list to include your desired websites, including their link shortener domains (nytimes.com, nyti.ms, etc). Run!

-

## Scheduling

Scheduling this script to run automatically in macOS can be done by following these steps:
1. Open the plist file and edit the path string to reflect the location of the script on your hard drive.
2. Place the plist file in your ~/Library/LaunchAgents folder.
3. Open a terminal, navigate to the directory containing this script, and run the following commands:
	chmod u+x HNtoInstapaper.py
	launchctl load ~/Library/LaunchAgents/net.assareh.hntoinstapaper.plist

Further information on launchd and launchctl can be found [here](https://nathangrigg.com/2012/07/schedule-jobs-using-launchd).