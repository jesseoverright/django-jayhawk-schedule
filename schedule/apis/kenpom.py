from django.core.cache import cache
import csv
import json
import os
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
            directory = os.path.dirname(__file__)

            kenpom_csv = open(directory + '/kenpom.csv','rU')

            csv_reader = csv.DictReader(kenpom_csv)

            # try a request
            #try:
            #    response = requests.get(url)
            #    csv_reader = response.text()
            #except request.exceptions.HTTPError as error:
            #    kenpom_stats = False

            data = json.dumps([row for row in csv_reader])
            kenpom_stats = json.loads(data)

            cache.set(cache_key, kenpom_stats)

        return kenpom_stats

    def get_team(self, team_name):
        team_name = team_name.replace("State", "St.")
        for team in self.kenpom_stats:
            if team['TeamName'] == team_name:
                return team

        return False