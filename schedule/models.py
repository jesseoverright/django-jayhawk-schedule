from django.db import models
from django.core.urlresolvers import reverse
import datetime
import json
import urllib2

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
        self.key = "q5vjgc6pmygdg3ufz3p9hw7c"
        url = "http://api.espn.com/v1/sports/basketball/mens-college-basketball/teams?apikey=%s&limit=351"

        try:
            response = urllib2.urlopen(url % self.key)
            data = json.load(response)
        except urllib2.HTTPError as error:
            data = False

        if data:
            self.teams =  data['sports'][0]['leagues'][0]['teams']
        else: 
            self.teams = []

    def get_team(self, team_name, mascot):
        for team in self.teams:
            if team['name'] == mascot and team['location'] == team_name:
                return team

        return False

    def get_team_news(self, team_id):
        url = "http://api.espn.com/v1/now?leagues=mens-college-basketball&teams=%s&apikey=%s"

        try:
            response = urllib2.urlopen(url % (team_id, self.key))
            data = json.load(response)
        except urllib2.HTTPError as error:
            data = False

        return data


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
        news = espn_api.get_team_news(self._get_espn_api_team_details()['id'])['feed']

        for article in news:
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

    