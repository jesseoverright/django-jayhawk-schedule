from django.core.cache import cache
import csv
import json
import os


class KenpomApi(object):
    def __init__(self):
        url = "http://kenpom.com/getdata.php?file=summary14"

        stats_cache_key = u'Kenpom-Stat-Dictionary'
        self.teams = cache.get(stats_cache_key)

        if not self.teams:
            kenpom_stats = self._get_kenpom_stats(url)

            self.teams = {}

            # iterate over list of json objects and create a dictionary using key: team name
            # this allows us to access teams by key value instead of iterating over entire list of objects
            if kenpom_stats:
                for team in kenpom_stats:
                    self.teams[team['TeamName']] = team
                cache.set(stats_cache_key, self.teams, 60*60*24)

    def _get_kenpom_stats(self, url):
        # only ingest kenpom file if results are not already cached
        cache_key = u'%s' % (url)
        cache_key = cache_key.replace(' ','')
        kenpom_stats = cache.get(cache_key)

        if not kenpom_stats:
            # look for file in immediate directory
            directory = os.path.dirname(__file__)

            kenpom_csv = open(directory + '/kenpom.csv','rU')

            csv_reader = csv.DictReader(kenpom_csv)

            # iterate over csv file and generate list of json objects
            data = json.dumps([row for row in csv_reader])
            kenpom_stats = json.loads(data)

            cache.set(cache_key, kenpom_stats)

        return kenpom_stats

    def get_team(self, team_name):
        # sanitize team name based on kenpom abbreviations
        team_name = team_name.replace("State", "St.")
        team_name = team_name.replace("-", " ")

        if team_name in self.teams:
            return self.teams[team_name]

        return False