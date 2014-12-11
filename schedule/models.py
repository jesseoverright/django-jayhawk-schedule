from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils import timezone
import datetime
from helpers import dedupe_lists

from schedule.apis import EspnApi, TwitterApi, KenpomApi


GAME_TYPES = (
    ('Exhibition', 'Exhibition'),
    ('Non Conference', 'Non-Conference'),
    ('Preseason Tournament', 'Preseason Tournament'),
    ('Conference', 'Conference'),
    ('Conference Tournament', 'Conference Tournament'),
    ('NCAA Tournament', 'NCAA Tournament'),
)

CONFERENCES = (
    ('Big 12', 'Big 12'),
    ('ACC', 'ACC'),
    ('PAC 12', 'PAC 12'),
    ('SEC', 'SEC'),
    ('Big 10', 'Big 10'),
    ('Big East', 'Big East'),
    ('Mountain West', 'Mountain West'),
    ('Conference USA', 'Conference USA'),
)

SEASONS = (
    ('2014-15', '2014-15'),
    ('2013-14', '2013-14'),
)

espn_api = EspnApi()
twitter_api = TwitterApi()
kenpom_api = KenpomApi()

class Team(models.Model):
    name = models.CharField(max_length=255)
    mascot = models.CharField(max_length=255)
    nickname = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(unique=True, max_length=255)
    conference = models.CharField(blank=True,max_length=255,choices=CONFERENCES)
    home_arena = models.CharField(max_length=512, blank=True)
    _espn_api_team_details = None
    kenpom_stats = None
    news = None
    game_recaps = None
    videos = None
    podcasts = None

    def __unicode__(self):
        return u'%s %s' % (self.name, self.mascot)

    def _get_kenpom_stats(self):
        if self.kenpom_stats is None:
            self.kenpom_stats = kenpom_api.get_team(self.name)
            return self.kenpom_stats
        else:
            return self.kenpom_stats

    def _get_espn_api_team_details(self):
        if self._espn_api_team_details is None:
            self._espn_api_team_details = espn_api.get_team(self.name, self.mascot)
            return self._espn_api_team_details
        else:
            return self._espn_api_team_details

    def get_ranking(self):
        if self._get_kenpom_stats():
            return int(self._get_kenpom_stats()['RankPythag'])
        else:
            return ''

    def get_offensive_efficiency(self):
        if self._get_kenpom_stats():
            per_possession = float(self._get_kenpom_stats()['AdjOE']) / 100
            return per_possession
        else:
            return ''

    def get_offensive_difference(self):
        return self.get_offensive_efficiency() - 1

    def get_defensive_efficiency(self):
        if self._get_kenpom_stats():
            per_possession = float(self._get_kenpom_stats()['AdjDE']) / 100
            return per_possession
        else:
            return ''

    def get_defensive_difference(self):
        return 1 - self.get_defensive_efficiency()

    def get_offensive_rank(self):
        if self._get_kenpom_stats():
            return int(self._get_kenpom_stats()['RankAdjOE'])
        else:
            return ''

    def get_defensive_rank(self):
        if self._get_kenpom_stats():
            return int(self._get_kenpom_stats()['RankAdjDE'])
        else:
            return ''

    def get_styled_name(self):
        if self.color():
            if self.get_ranking():
                return u'<span style="color:#%s">%s %s %s</span>' % (self.color(), self.get_ranking(), self.name, self.mascot)
            else:
                return u'<span style="color:#%s">%s %s</span>' % (self.color(), self.name, self.mascot)
        else:
            if self.get_ranking():
                return u'%s %s %s' % (self.get_ranking(), self.name, self.mascot)
            else:
                return self

    def get_nickname(self):
        if self.nickname:
            return self.nickname
        else:
            return self.name

    def espn_link(self):
        return self._get_espn_api_team_details()['links']['web']['teams']['href']

    def color(self):
        if self._get_espn_api_team_details():
            return self._get_espn_api_team_details()['color']

        return False

    def get_tweets(self):
        return twitter_api.get_team_tweets(self.name, self.mascot)

    def get_absolute_url(self):
        return reverse('schedule.views.team', args=[self.slug])


# a Game is a matchup between two teams, including team and opponenet, date, location,
# tv details, game type, scores, news, videos, podcasts and game recaps
class Game(models.Model):
    team, created = Team.objects.get_or_create(slug=settings.SCHEDULE_SETTINGS['team']['slug'])
    opponent = models.ForeignKey(Team)
    slug = models.SlugField(unique=True, max_length=255)
    location = models.CharField(max_length=255, blank=True)
    television = models.CharField(max_length=255, blank=True)
    date = models.DateTimeField()
    season = models.CharField(max_length=7, choices=SEASONS)
    game_type = models.CharField(max_length=25, choices=GAME_TYPES)
    score = models.IntegerField(null=True, blank=True)
    opponent_score = models.IntegerField(null=True, blank=True)
    overtime = models.BooleanField()
    news = None
    game_recaps = None
    videos = None
    podcasts = None

    class Meta:
        ordering = ['-date']

    def __unicode__(self):
        game_date = timezone.localtime(self.date)
        return u'%s %s' % (self.opponent.name, game_date.strftime('%b %d'))

    def get_result(self):
        if self.score > self.opponent_score:
            return 'win'
        elif self.score < self.opponent_score:
            return 'loss'
        else:
            return False

    def get_endtime(self):
        return self.date + datetime.timedelta(0,9000)

    def get_matchup(self):
        if self.location == self.team.home_arena:
            return '%s at %s' % (self.opponent.get_styled_name(), self.team.get_styled_name())

        return '%s vs %s' % (self.team.get_styled_name(), self.opponent.get_styled_name())

    def get_ical_summary(self):
        if self.get_result() != False:
            summary = self.get_result()[0].upper() + ' ' + str(self.score) + '-' + str(self.opponent_score) + ' '
        else:
            summary = ''

        if self.overtime:
            summary += ' (OT) '

        if self.location == self.team.home_arena:
            summary += self.opponent.get_nickname() + ' at ' + self.team.get_nickname()
        else:
            summary += self.team.get_nickname() + ' vs ' + self.opponent.get_nickname()

        return u'%s' % summary

    def get_game_type(self):
        game_type = self.game_type
        if self.game_type == 'Non Conference' or self.game_type == 'Conference':
            if self.team.home_arena == self.location:
                game_type += ' Home Game'
            else:
                game_type += ' Away Game'

        return game_type


    def get_tweets(self):
        return twitter_api.get_game_tweets(self.team.name, self.team.mascot, self.team.get_nickname(), self.opponent.name, self.opponent.mascot, self.date)

    def get_absolute_url(self):
        return reverse('schedule.views.game', args=[self.season, self.slug])


