from django.conf import settings
from django.core.cache import cache
import requests
from datetime import datetime

class EspnApi(object):
    def __init__(self):
        self.key = getattr(settings, "ESPN_API_KEY", None)
        url = "http://api.espn.com/v1/sports/basketball/mens-college-basketball/teams"
        params = {'apikey': self.key,
                  'limit': 351,
                  }

        # load cached team dictionary if it exists
        team_cache_key = u'Team-Dictionary'
        self.teams = cache.get(team_cache_key)

        if not self.teams:
            all_teams = self._get_results(url, params)

            self.teams = {}

            if all_teams:
                team_list =  all_teams['sports'][0]['leagues'][0]['teams']

                # iterate over list of json objects and create a dictionary using key: team location
                # this allows us to access teams by key value instead of iterating over entire list of objects
                for team in team_list:
                    self.teams[team['location']] = team
                cache.set(team_cache_key, self.teams, 60*60*30)

    def _get_results(self, url, params, cache_timeout=getattr(settings, "CACHE_TIMEOUT", None)):
        # only access espn api if results of particular query are not already cached
        cache_key = u'%s%s' % (url, str(params))
        cache_key = cache_key.replace(' ','')
        json_results = cache.get(cache_key)

        if not json_results:

            try:
                response = requests.get(url, params=params)
                json_results = response.json()
            except requests.exceptions.HTTPError as error:
                json_results = False

            cache.set(cache_key, json_results, cache_timeout)

        return json_results

    def get_team(self, team_name, mascot):
        if team_name in self.teams:
            return self.teams[team_name]

        return False

    def get_team_updates(self, team_id, content='blog,podcast,story,video', limit=7):
        url = "http://api.espn.com/v1/now"
        params = {'leagues': 'mens-college-basketball',
                  'teams': team_id,
                  'apikey': self.key,
                  'limit': limit,
                  'content': content,
                  }

        return self._get_results(url, params)

    def get_game_recaps(self, team_id, date=datetime.now().strftime('%Y%m%d'), limit=7):
        url = "http://api.espn.com/v1/sports/basketball/mens-college-basketball/teams/%s/news" % team_id
        params = {'apikey': self.key,
                  'limit': limit,
                  'dates': date,
                  }

        return self._get_results(url, params, 60*60*48)