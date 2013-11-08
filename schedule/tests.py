import datetime
from django.utils import timezone

from django.test import TestCase
from schedule.models import Game

class GamesTest(TestCase):
    def setUp(self):
        self.game = Game.objects.create(
            opponent='Memphis',
            slug='memphis',
            mascot='Tigers',
            date=timezone.make_aware(datetime.datetime.now(), timezone.get_default_timezone()),
            score=75,
            opponent_score=68,
            )
    def test_game_result(self):
        self.assertEqual(self.game.result(), 'win') 