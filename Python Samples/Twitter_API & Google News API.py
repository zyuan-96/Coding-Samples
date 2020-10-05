import json
import csv
import tweepy
import re
from datetime import datetime

def search_for_hashtags(consumer_key, consumer_secret, access_token, 
                        access_token_secret, hashtag_phrase):
    """
    INPUTS:
        consumer_key, consumer_secret, access_token, access_token_secret: codes 
        from twitter API that shows the authorizaion
        hashtag_phrase: a hashtag or the combination of hashtags
    """
    # Create authentication for accessing Twitter
    # (ref:https://developer.twitter.com/en/docs)
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    # Initialize Tweepy API
    api = tweepy.API(auth)
    
    # Name the csv file
    fname = '_'.join(re.findall(r"#(\w+)", hashtag_phrase))

    with open('%s.csv' % (fname), 'w', encoding="utf-8") as file:

        w = csv.writer(file)

        # Write header rows with selected variables
        w.writerow(['timestamp', 'tweet_text', 'username', 'all_hashtags', 
                    'followers_count', 'location', 'tweet_count', 
                    'verified_account', 'coordinates', 
                    'favorite_count', 'retweet_count'])

        # Write relevant info for the matching tweets
        for tweet in tweepy.Cursor(api.search, 
                                   q=hashtag_phrase+' -filter:retweets', 
                                   lang="en", tweet_mode='extended').items(2): 
        #Number of tweets could be changed here
            w.writerow([tweet.created_at, tweet.full_text.replace('\n',' '), 
                        tweet.user.screen_name, 
                        [e['text'] for e in tweet._json['entities']['hashtags']], 
                        tweet.user.followers_count, 
                        tweet.user.location, tweet.user.statuses_count, 
                        tweet.user.verified, tweet.coordinates, 
                        tweet.favorite_count, tweet.retweet_count])
            

c_k = 'pgR8j3XLa25kQGcJOJPlXiVrw'
c_s = 'VGjhVL8Iok6dBoQ0Cda0aRWirFiwP6cAZPlSJEUAvbQKqoRsAT'
a_t = '792789486-OvGs9HtHDegoppStyGkA2jc22PVqB7nT9XxAQOo1'
a_ts = 'PtQ8sicubEZHIXyMY7MoZKpDhdYbtwfi7CXWl1KNyutg2'
Hashtags = ['#coronavirus', '#COVID19', '#wuhancoronavirus', 
            '#coronavirus AND #US', '#coronavirus AND #japan', 
            '#COVID19 AND #US','#coronavirus AND #wuhan',
            '#coronavirus AND #hongkong', '#coronavirus AND #LA', 
            '#coronavirus AND #CHICAGO','#coronavirus AND #NY', 
            '#COVID19 AND #ITALY', '#coronavirus AND #ITALY', 
            '#COVID19 AND #Korea', '#coronavirus AND #Korea']
status = input('Status')

if __name__ == '__main__':
    if status == 'list':
        for tag in Hashtags:
            search_for_hashtags(c_k, c_s, a_t, a_ts, tag)
    else:
        hashtag_phrase = input('Hashtag Phrase')
        search_for_hashtags(c_k, c_s, a_t, a_ts, hashtag_phrase)


'''
Get News from 9 sources through google news api
'''

from newsapi import NewsApiClient
import csv
import pandas as pd
#Setting the google news api user key
newsapi = NewsApiClient(api_key='2fd12bd819ec4bd79434f7b150f0d4ba')
#getting the dates that are targeted to scape news from
dates = []
#The limit is getting the news 1 month back
[dates.append('2020-02-'+ str(i)) for i in range(11,30)]
#specifying the 9 targeted sources
media_list = ['cnn', 'cnbc','reuters', 'the-wall-street-journal','bloomberg',
              'the-washington-post','the-verge','vice-news','buzzfeed']


def get_news(media_name):
    '''
    Getting the news from the google news api
    '''
    all_articles = []
    for j in dates:
        one_article = newsapi.get_everything(q='coronavirus',
                                             sources= media_name,
                                             from_param= j,
                                             to= j,
                                             language='en',
                                             sort_by='popularity',
                                             page=1)
        all_articles.append(one_article)
    x = all_articles
    return x




def write_news(media_list):
    '''
    Getting the news from the targeted media source list,
    then return cvs files for each source.
    '''
    for s in media_list:
        x = get_news(s)
        with open(str(s) + 'news_data.csv', 'w', encoding="utf-8") as csv_file:
            newswriter = csv.writer(csv_file)
            newswriter.writerow(['title_text', 'Time_stamp','source'])
            for arti in x:
                for k in arti['articles']:
                    newswriter.writerow([k['title'],k['description'],
                                         k['publishedAt'], s])


##################
##Execution

write_news(media_list)
