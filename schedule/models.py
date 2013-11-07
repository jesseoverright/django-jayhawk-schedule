from django.db import models
from django.core.urlresolvers import reverse

# a Game on KU's schedule includes opponent info, date, location and tv details
class Game(models.Model):
    opponent = models.CharField(max_length=255)
    mascot = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255)
    location = models.CharField(max_length=255)
    television = models.CharField(max_length=255)
    date = models.DateTimeField()
    game_type = models.CharField(max_length=25)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ['-date']

    def __unicode__(self):
        return u'%s' % self.opponent

    def get_absolute_url(self):
        return reverse('schedule.views.game', args=[self.slug])