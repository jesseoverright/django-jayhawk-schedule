from django.conf import settings
from django.core.cache import cache
import requests

class EspnApi(object):
    def __init__(self):
        self.key = getattr(settings, "ESPN_API_KEY", None)
        url = "http://api.espn.com/v1/sports/basketball/mens-college-basketball/teams"
        params = {'apikey': self.key,
                  'limit': 351,
                  }

        all_teams = self._get_results(url, params)

        if all_teams:
            self.teams =  all_teams['sports'][0]['leagues'][0]['teams']
        else: 
            self.teams = []

    def _get_results(self, url, params):
        cache_key = u'%s%s' % (url, str(params))
        cache_key = cache_key.replace(' ','')
        json_results = cache.get(cache_key)

        if not json_results:

            try:
                response = requests.get(url, params=params)
                json_results = response.json()
            except request.exceptions.HTTPError as error:
                json_results = False

            cache.set(cache_key, json_results)

        return json_results

    def get_team(self, team_name, mascot):
        for team in self.teams:
            if team['name'] == mascot and team['location'] == team_name:
                return team

        return False

    def get_team_news(self, team_id):
        url = "http://api.espn.com/v1/now"
        params = {'leagues': 'mens-college-basketball',
                  'teams': team_id,
                  'apikey': self.key,
                  'limit': 7,
                  }

        return self._get_results(url, params)