from django.core.cache import cache
import csv
import json
#import requests


class KenpomApi(object):
    def __init__(self):
        url = "http://kenpom.com/getdata.php?file=summary14"
        self.kenpom_stats = self._get_kenpom_stats(url)

    def _get_kenpom_stats(self, url):
        cache_key = u'%s' % (url)
        cache_key = cache_key.replace(' ','')
        kenpom_stats = cache.get(cache_key)

        if not kenpom_stats:

            kenpom_csv = open('kenpom.csv','rU')

            reader = csv.DictReader(kenpom_csv)

            data = json.dumps([row for row in reader])
            kenpom_stats = json.loads(data)

            # try a request
            #try:
            #    response = requests.get(url)
            #    kenpom_stats = response.json()
            #except request.exceptions.HTTPError as error:
            #    kenpom_stats = False

            cache.set(cache_key, kenpom_stats)

        return kenpom_stats

    def get_team(self, team_name):
        for team in self.kenpom_stats:
            if team['TeamName'] == team_name:
                return team

        return False