import datetime
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings

from django.test import TestCase
from schedule.models import Game, EspnApi

class GamesTest(TestCase):
    def setUp(self):
        self.game = Game.objects.create(
            opponent='Memphis',
            slug='memphis',
            mascot='Tigers',
            date=timezone.make_aware(datetime.datetime(2008, 04, 07), timezone.get_default_timezone()),
            score=75,
            opponent_score=68,
            )
    def test_game_result(self):
        self.assertEqual(self.game.get_result(), 'win') 
    def test_game_summary(self):
        self.assertEqual(self.game.get_summary(), 'W 75-68 KU vs Memphis')
    def test_team_ESPN_link(self):
        self.assertIsNotNone(self.game.get_espn_link)
    def test_team_articles(self):
        self.game.get_team_articles()
        self.assertIsNotNone(self.game.team_videos)
        self.assertIsNotNone(self.game.team_news)
    def test_game_title(self):
        self.assertEqual(u'%s' % self.game, u'Memphis Apr 07')
    def test_espn_api_cache(self):
        self.espn_api = EspnApi()
        url = "http://api.espn.com/v1/sports/basketball/mens-college-basketball/teams"
        params = {'apikey': getattr(settings, "ESPN_API_KEY", None),
                  'limit': 351,
                  }
        cache_key = u'%s%s' % (url, str(params))

        self.assertEqual(cache.get(cache_key)['sports'][0]['leagues'][0]['teams'], self.espn_api.teams)