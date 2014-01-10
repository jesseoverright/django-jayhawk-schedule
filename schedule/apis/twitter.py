from django.conf import settings
from django.core.cache import cache
import datetime
import requests
import re

from rauth import OAuth1Service

class TwitterApi(object):
    def __init__(self):
        self.keys = getattr(settings, "TWITTER_API_KEYS", None)
        self.twitter_api = OAuth1Service(
            name='twitter',
            consumer_key=self.keys['consumer_key'],
            consumer_secret=self.keys['consumer_secret'],
            request_token_url='https://api.twitter.com/oauth/request_token',
            access_token_url='https://api.twitter.com/oauth/access_token',
            authorize_url='https://api.twitter.com/oauth/authorize',
            base_url='https://api.twitter.com/1.1/')

    def _get_tweets(self, params):
        cache_key = u'%s' % str(params)
        cache_key = cache_key.replace(' ','')
        tweet_results = cache.get(cache_key)

        if not tweet_results:

            self.session = self.twitter_api.get_session((self.keys['access_token'], self.keys['access_token_secret']))

            api_response = self.session.get('search/tweets.json', params=params, verify=True)

            # get all tweets if no popular tweets exist
            if not 'statuses' in api_response:
                params['result_type'] = 'mixed'
                api_response = self.session.get('search/tweets.json', params=params, verify=True)

            tweet_results = api_response.json()['statuses']

            cache.set(cache_key, tweet_results)

        return tweet_results

    def get_team_tweets(self, team_name, team_mascot):
        params = {'q': team_name + ' ' + team_mascot,
                  'count': 15,
                  'result_type': 'popular'
                  }

        statuses = self._get_tweets(params)

        for tweet in statuses:
            # add anchor tags to links in tweet
            tweet['text'] = re.sub(r'((https?|s?ftp|ssh)\:\/\/[^"\s\<\>]*[^.,;\'">\:\s\<\>\)\]\!])', r'<a href="\1">\1</a>', tweet['text'])
            # add anchor tags to hashtags
            tweet['text'] = re.sub(r'#([_a-zA-Z0-9]+)', r'<a href="http://twitter.com/search?q=\1">#\1</a>', tweet['text'])
            # add anchor tags to mentions
            tweet['text'] = re.sub(r'@([_a-zA-Z0-9]+)', r'<a href="http://twitter.com/\1">@\1</a>', tweet['text'])
            # convert date to relative date
            # Sun Nov 17 18:00:04 +0000 2013
            tweet['created_at'] = datetime.datetime.strptime(tweet['created_at'][0:19], '%a %b %d %H:%M:%S')

        return statuses