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
                  'apikey': self.key
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

        self.session = self.twitter_api.get_session((self.keys['access_token'], self.keys['access_token_secret']))

    def get_tweets(self, team_name, team_mascot): 
        params = {'q': team_name + ' ' + team_mascot,
                  'count': 10,
                  'result_type': 'popular'
                  }

        r = self.session.get('search/tweets.json', params=params, verify=True)

        statuses = r.json()['statuses']

        for tweet in statuses:
            # add anchor tags to links in tweet
            tweet['text'] = re.sub(r'((https?|s?ftp|ssh)\:\/\/[^"\s\<\>]*[^.,;\'">\:\s\<\>\)\]\!])', r'<a href="\1">\1</a>', tweet['text'])
            # add anchor tags to hashtags
            # add anchor tags to mentions
        
        return statuses

espn_api = EspnApi()

# a Game on KU's schedule includes opponent info, date, location and tv details
class Game(models.Model):
    opponent = models.CharField(max_length=255)
    mascot = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    location = models.CharField(max_length=255)
    television = models.CharField(max_length=255)
    date = models.DateTimeField()
    game_type = models.CharField(max_length=25, choices=GAME_TYPES)
    score = models.IntegerField(null=True, blank=True)
    opponent_score = models.IntegerField(null=True, blank=True)
    _espn_api_team_details = None
    team_news = None
    team_videos = None

    class Meta:
        ordering = ['-date']

    def __unicode__(self):
        return u'%s %s' % (self.opponent, self.date.strftime('%b %d'))

    def _get_espn_api_team_details(self):
        if self._espn_api_team_details is None:
            self._espn_api_team_details = espn_api.get_team(self.opponent, self.mascot)
            return self._espn_api_team_details
        else:
            return self._espn_api_team_details

    def _get_espn_api_team_articles(self):
        if self._get_espn_api_team_details() != False:
            news = espn_api.get_team_news(self._get_espn_api_team_details()['id'])

            if news:
                for article in news['feed']:
                    if 'type' in article.keys() and article['type'] == "Media":
                        self.team_videos.append(article)
                    else:
                        self.team_news.append(article)

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
            summary += self.opponent + ' at KU'
        else:
            summary += 'KU vs ' + self.opponent

        return u'%s' % summary

    def get_espn_link(self):
        return self._get_espn_api_team_details()['links']['web']['teams']['href']

    def get_team_color(self):
        return self._get_espn_api_team_details()['color']

    def get_team_articles(self):
        if self.team_news is None and self.team_videos is None:
            self.team_news = []
            self.team_videos = []

            self._get_espn_api_team_articles()

    def get_absolute_url(self):
        return reverse('schedule.views.game', args=[self.slug])

    def get_tweets(self):
        twitter_api = TwitterApi()
        return twitter_api.get_tweets(self.opponent, self.mascot)


    