import datetime
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings

from django.test import TestCase
from schedule.models import Game, EspnApi, TwitterApi

import re

class GamesTest(TestCase):
    def setUp(self):
        self.game = Game.objects.create(
            opponent='Memphis',
            slug='memphis',
            mascot='Tigers',
            location='Alamodome, San Antonio, TX',
            date=timezone.make_aware(datetime.datetime(2008, 04, 07), timezone.get_default_timezone()),
            score=75,
            opponent_score=68,
            )

    def test_homepage_renders_correct_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'schedule/index.html')

    def test_game_page_renders_correct_template(self):
        response = self.client.get('/memphis/')
        self.assertTemplateUsed(response, 'schedule/game.html')

    def test_is_game_result_accurate(self):
        self.assertEqual(self.game.get_result(), 'win') 

    def test_game_summary(self):
        self.assertEqual(self.game.get_summary(), 'W 75-68 KU vs Memphis')

    def test_has_ESPN_link(self):
        self.assertIsNotNone(self.game.get_espn_link)

    def test_get_team_color(self):
        self.assertEqual(self.game.get_team_color(), '002447')

    def test_has_team_articles(self):
        self.game.get_team_articles()
        self.assertIsNotNone(self.game.team_videos)
        self.assertIsNotNone(self.game.team_news)

    def test_game_title(self):
        self.assertEqual(u'%s' % self.game, u'Memphis Apr 07')

    def test_is_espn_api_result_caching(self):
        self.espn_api = EspnApi()

        url = "http://api.espn.com/v1/sports/basketball/mens-college-basketball/teams"
        params = {'apikey': getattr(settings, "ESPN_API_KEY", None),
                  'limit': 351,
                  }
        cache_key = u'%s%s' % (url, str(params))
        cache_key = cache_key.replace(' ','')

        self.assertEqual(cache.get(cache_key)['sports'][0]['leagues'][0]['teams'], self.espn_api.teams)

    def test_is_twitter_api_result_caching(self):
        self.twitter_api = TwitterApi()
        self.game.get_team_tweets()

        params = {'q': self.game.opponent + ' ' + self.game.mascot,
                  'count': 15,
                  'result_type': 'popular'
                  }

        cache_key = u'%s' % str(params)
        cache_key = cache_key.replace(' ','')

        self.assertEqual(cache.get(cache_key), self.twitter_api._get_tweets(params))

    def test_regex_for_web_links(self):
        tweet = "A closer look at Duke's first national ranking since Dec. 6, 1994. One writer had the Blue Devils as high as No. 21 https://t.co/1VJegEg3CY"

        tweet = re.sub(r'((https?|s?ftp|ssh)\:\/\/[^"\s\<\>]*[^.,;\'">\:\s\<\>\)\]\!])', r'<a href="\1">\1</a>', tweet)

        self.assertEqual(tweet, "A closer look at Duke's first national ranking since Dec. 6, 1994. One writer had the Blue Devils as high as No. 21 <a href=\"https://t.co/1VJegEg3CY\">https://t.co/1VJegEg3CY</a>")