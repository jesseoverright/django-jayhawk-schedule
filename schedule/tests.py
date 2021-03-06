import datetime
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings

from django.test import TestCase
from schedule.models import Team, Game
from schedule.apis import KenpomApi, EspnApi, TwitterApi

import re

class KenpomTests(TestCase):
    def setUp(self):
        self.team = Team.objects.create(
            name='Kansas',
            mascot='Jayhawks',
            slug='kansas-jayhawks'
            )

    def test_kenpom_team_dictionary(self):
        self.kenpom_api = KenpomApi()

        self.assertEqual(self.kenpom_api.teams[self.team.name]['TeamName'], 'Kansas')

class EspnApiTests(TestCase):
    def setUp(self):
        self.team = Team.objects.create(
            name='Kansas',
            mascot='Jayhawks',
            slug='kansas-jayhawks'
            )

    def test_is_espn_api_result_caching(self):
        self.espn_api = EspnApi()

        url = "http://api.espn.com/v1/sports/basketball/mens-college-basketball/teams"
        params = {'apikey': getattr(settings, "ESPN_API_KEY", None),
                  'limit': 351,
                  }
        cache_key = u'%s%s' % (url, str(params))
        cache_key = cache_key.replace(' ','')

        team_list = cache.get(cache_key)
        if 'sports' in team_list.keys():
            team_list = team_list['sports'][0]['leagues'][0]['teams']
        cache_teams = {}
        for team in team_list:
            cache_teams[team['location']] = team

        self.assertEqual(cache_teams, self.espn_api.teams)

    def test_espn_api_team_dictionary(self):
        self.espn_api = EspnApi()

        self.assertEqual(self.espn_api.teams[self.team.name]['name'],'Jayhawks')

class TwitterApiTests(TestCase):
    def setUp(self):
        self.team = Team.objects.create(
            name='Kansas',
            mascot='Jayhawks',
            slug='kansas-jayhawks'
            )

    def test_is_twitter_api_result_caching(self):
        self.twitter_api = TwitterApi()
        self.team.get_tweets()

        params = {'q': self.team.name + ' ' + self.team.mascot,
                  'count': 15,
                  'result_type': 'popular'
                  }

        cache_key = u'%s' % str(params)
        cache_key = cache_key.replace(' ','')

        tweets = self.twitter_api._get_tweets(params)

        self.assertEqual(cache.get(cache_key), tweets)

    def test_regex_for_web_links(self):
        tweet = "A closer look at Duke's first national ranking since Dec. 6, 1994. One writer had the Blue Devils as high as No. 21 https://t.co/1VJegEg3CY"

        tweet = re.sub(r'((https?|s?ftp|ssh)\:\/\/[^"\s\<\>]*[^.,;\'">\:\s\<\>\)\]\!])', r'<a href="\1">\1</a>', tweet)

        self.assertEqual(tweet, "A closer look at Duke's first national ranking since Dec. 6, 1994. One writer had the Blue Devils as high as No. 21 <a href=\"https://t.co/1VJegEg3CY\">https://t.co/1VJegEg3CY</a>")

class GameTests(TestCase):
    def setUp(self):
        team = Team.objects.create(
            name='Memphis',
            mascot='Tigers',
            slug='memphis-tigers'
            )
        self.game = Game.objects.create(
            opponent=team,
            slug='2008-championship',
            location='Alamodome, San Antonio, TX',
            date=timezone.make_aware(datetime.datetime(2008, 04, 07, 8), timezone.get_default_timezone()),
            score=75,
            opponent_score=68,
            )

    def test_homepage_renders_correct_template(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'schedule/index.html')

    def test_game_page_renders_correct_template(self):
        response = self.client.get('/2008-championship/')
        self.assertTemplateUsed(response, 'schedule/game.html')

    def test_team_page_renders_correct_template(self):
        response = self.client.get('/team/memphis-tigers/')
        self.assertTemplateUsed(response,'schedule/team.html')

    def test_is_game_result_accurate(self):
        self.assertEqual(self.game.get_result(), 'win')

    def test_ical_summary(self):
        self.assertEqual(self.game.get_ical_summary(), 'W 75-68 KU vs Memphis')

    def test_has_ESPN_link(self):
        self.assertIsNotNone(self.game.opponent.espn_link)

    def test_is_team_color_correct(self):
        self.assertEqual(self.game.opponent.color(), '002447')

    def test_is_team_styled_name_correct(self):
        self.assertEqual(self.game.opponent.get_styled_name(), u'<span style="color:#002447">25 Memphis Tigers</span>')
        no_api_team = Team.objects.create(
            name='Harlem',
            mascot='Globetrotters',
            slug='harlem-globetrotters',
            )
        self.assertEqual(u'%s' % no_api_team.get_styled_name(), 'Harlem Globetrotters')

    def test_has_team_articles(self):
        self.game.opponent.get_news(1)
        self.game.opponent.get_videos(1)
        self.game.opponent.get_podcasts(1)
        self.assertIsNotNone(self.game.opponent.videos)
        self.assertIsNotNone(self.game.opponent.news)
        self.assertIsNotNone(self.game.opponent.podcasts)

    def test_game_title(self):
        self.assertEqual(u'%s' % self.game, u'Memphis Apr 07')