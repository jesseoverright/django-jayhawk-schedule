from django.db import models
from django.core.urlresolvers import reverse
import datetime

GAME_TYPES = (
    ('Exhibition', 'Exhibition'),
    ('Non Conference', 'Non-Conference'),
    ('Preseason Tournament', 'Preseason Tournament'),
    ('Conference', 'Conference'),
    ('Conference Tournament', 'Conference Tournament'),
    ('NCAA Tournament', 'NCAA Tournament'),
)

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

    def game_end(self):
        return self.date + datetime.timedelta(0,9000)

    def result(self):
        if self.score > self.opponent_score:
            return 'win'
        elif self.score < self.opponent_score:
            return 'loss'
        else:
            return False

    class Meta:
        ordering = ['-date']

    def __unicode__(self):
        return u'%s %s' % (self.opponent, self.date.strftime('%b %d'))

    def get_absolute_url(self):
        return reverse('schedule.views.game', args=[self.slug])