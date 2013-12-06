from django.db import models
from django.core.urlresolvers import reverse
import datetime

from schedule.apis import EspnApi, TwitterApi


GAME_TYPES = (
    ('Exhibition', 'Exhibition'),
    ('Non Conference', 'Non-Conference'),
    ('Preseason Tournament', 'Preseason Tournament'),
    ('Conference', 'Conference'),
    ('Conference Tournament', 'Conference Tournament'),
    ('NCAA Tournament', 'NCAA Tournament'),
)

espn_api = EspnApi()
twitter_api = TwitterApi()

class Team(models.Model):
    name = models.CharField(max_length=255)
    mascot = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    conference = models.CharField(max_length=255)
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

    def get_colored_name(self):
        if self.color():
            return u'<span style="color:#%s">%s %s</span>' % (self.color(), self.name, self.mascot)

        return u'%s %s' % (self.name, self.mascot)

    def espn_link(self):
        return self._get_espn_api_team_details()['links']['web']['teams']['href']

    def color(self):
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
        return u'%s %s' % (self.opponent.name, self.date.strftime('%b %d'))

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
        if self.location == "Allen Fieldhouse, Lawrence, KS":
            return '%s at Kansas Jayhawks' % self.opponent.get_colored_name()
        
        return 'Kansas Jayhawks vs %s' % self.opponent.get_colored_name()

    def get_ical_summary(self):
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


    