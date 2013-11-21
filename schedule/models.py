from django.db import models
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.conf import settings
from rauth import OAuth1Service
import datetime
import requests
import re

GAME_TYPES = (
    ('Exhibition', 'Exhibition'),
    ('Non Conference', 'Non-Conference'),
    ('Preseason Tournament', 'Preseason Tournament'),
    ('Conference', 'Conference'),
    ('Conference Tournament', 'Conference Tournament'),
    ('NCAA Tournament', 'NCAA Tournament'),
)

class EspnApi(object):
    def __init__(self):
        self.key = getattr(settings, "ESPN_API_KEY", None)
        url = "http://api.espn.com/v1/sports/basketball/mens-college-basketball/teams"
        params = {'apikey': self.key,
                  'limit': 351,
                  }

        all_teams = self._get_results(url, params)

        if all_teams:
            self.teams =  all_teams['sports'][0]['leagues'][0]['teams']
        else: 
            self.teams = []

    def _get_results(self, url, params):
        cache_key = u'%s%s' % (url, str(params))
        json_results = cache.get(cache_key)

        if not json_results:

            try:
                response = requests.get(url, params=params)
                json_results = response.json()
            except request.exceptions.HTTPError as error:
                json_results = False

            cache.set(cache_key, json_results)

        return json_results

    def get_team(self, team_name, mascot):
        for team in self.teams:
            if team['name'] == mascot and team['location'] == team_name:
                return team

        return False

    def get_team_news(self, team_id):
        url = "http://api.espn.com/v1/now"
        params = {'leagues': 'mens-college-basketball',
                  'teams': team_id,
                  'apikey': self.key,
                  'limit': 7,
                  }

        return self._get_results(url, params)

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

espn_api = EspnApi()
twitter_api = TwitterApi()

class Team(models.Model):
    name = models.CharField(max_length=255)
    mascot = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    _espn_api_team_details = None
    news = None
    videos = None

    def __unicode__(self):
        return u'%s %s' % (self.name, self.mascot)

    def _get_espn_api_team_details(self):
        if self._espn_api_team_details is None:
            self._espn_api_team_details = espn_api.get_team(self.name, self.mascot)
            return self._espn_api_team_details
        else:
            return self._espn_api_team_details

    def _get_espn_api_news(self):
        if self._get_espn_api_team_details() != False:
            news = espn_api.get_team_news(self._get_espn_api_team_details()['id'])

            if news:
                for article in news['feed']:
                    if 'type' in article.keys() and article['type'] == "Media":
                        self.videos.append(article)
                    else:
                        self.news.append(article)

    def espn_link(self):
        return self._get_espn_api_team_details()['links']['web']['teams']['href']

    def team_color(self):
        return self._get_espn_api_team_details()['color']

    def get_news(self):
        if self.news is None and self.videos is None:
            self.news = []
            self.videos = []

            self._get_espn_api_news()

    def get_tweets(self):
        return twitter_api.get_team_tweets(self.name, self.mascot)


# a Game on KU's schedule includes opponent, date, location and tv details
class Game(models.Model):
    opponent = models.ForeignKey(Team)
    slug = models.SlugField(unique=True, max_length=255)
    location = models.CharField(max_length=255)
    television = models.CharField(max_length=255)
    date = models.DateTimeField()
    game_type = models.CharField(max_length=25, choices=GAME_TYPES)
    score = models.IntegerField(null=True, blank=True)
    opponent_score = models.IntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['-date']

    def __unicode__(self):
        return u'%s %s' % (self.opponent, self.date.strftime('%b %d'))

    def get_result(self):
        if self.score > self.opponent_score:
            return 'win'
        elif self.score < self.opponent_score:
            return 'loss'
        else:
            return False

    def get_endtime(self):
        return self.date + datetime.timedelta(0,9000)

    def get_summary(self):
        if self.get_result() != False:
            summary = self.get_result()[0].upper() + ' ' + str(self.score) + '-' + str(self.opponent_score) + ' '
        else:
            summary = ''

        if self.location == "Allen Fieldhouse, Lawrence, KS":
            summary += self.opponent.name + ' at KU'
        else:
            summary += 'KU vs ' + self.opponent.name

        return u'%s' % summary

    def get_absolute_url(self):
        return reverse('schedule.views.game', args=[self.slug])


    