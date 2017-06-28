# HNtoInstapaper
*Find top articles on [Hacker News](http://news.ycombinator.com) from sites you like and automatically save them to Instapaper to read later.*

The @newsyc100 Twitter account tweets links posted to Hacker News that have earned 100 or more points.

I like reading The New Yorker and The Atlantic, but this script can be used for any websites. This script checks the last 200 tweets from the @newsyc100 Twitter account, looks for links to New Yorker and Atlantic articles, and then sends any results to your Instapaper account.

It will log the unique ID of the most recent scanned tweet so subsequent runs will be much faster.

To use, populate your Twitter API credentials and Instapaper account credentials. Edit the TARGET_URLS list to include your desired websites, including their link shortener domains (nytimes.com, nyti.ms, etc). Run!

## Scheduling

In macOS or Linux, this script can be scheduled to run automatically using [Cron](https://en.wikipedia.org/wiki/Cron). I have mine configured to run daily at midnight. Here's how:

1. Launch a terminal and execute ```crontab -e```
2. Add the following line to the cron file, editing the path to reflect the correct path on your machine:
```
0 0 * * * /path/to/HNtoInstapaper.py
```
3. Save and exit the editor.