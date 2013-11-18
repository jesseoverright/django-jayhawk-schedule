import datetime
from django.utils import timezone

from django.test import TestCase
from schedule.models import Game

import re

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

    def test_regex_for_web_links(self):
        tweet = "A closer look at Duke's first national ranking since Dec. 6, 1994. One writer had the Blue Devils as high as No. 21 https://t.co/1VJegEg3CY"

        tweet = re.sub(r'((https?|s?ftp|ssh)\:\/\/[^"\s\<\>]*[^.,;\'">\:\s\<\>\)\]\!])', r'<a href="\1">\1</a>', tweet)

        self.assertEqual(tweet, "A closer look at Duke's first national ranking since Dec. 6, 1994. One writer had the Blue Devils as high as No. 21 <a href=\"https://t.co/1VJegEg3CY\">https://t.co/1VJegEg3CY</a>")

