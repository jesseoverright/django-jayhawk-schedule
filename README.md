#Jayhawk Schedule

This is a simple django app built to track the __Kansas Jayhawks 2013-14__ basketball schedule.  The __Kansas Jayhawks 2013-14 Basketball Schedule__ provides all the latest news, videos, tweets and results for the Jayhawks season. You can view the project live at [http://jayhawkschedule.co](http://jayhawkschedule.co).

Main Features:

- gives admin ability to create games, set opponent, location, tv info
- utilizes the [ESPN API](http://developer.espn.com/docs) for video, team news, stats, and details
- utilizes the [Twitter API](https://dev.twitter.com/docs/api/1.1/get/search/tweets) to display latest tweets about each team.
- generates a ical calendar feed
- update results as games occur

## Jayhawk Schedule Homepage
![Jayhawk Schedule Homepage](https://raw.github.com/jesseoverright/django-jayhawk-schedule/master/jayhawkschedule/static/images/home-page.png)
The homepage displays the full list of games, including results, upcoming games, location, television info and more at a glance.

## Team Pages
![Jayhawk Schedule Team Page](https://raw.github.com/jesseoverright/django-jayhawk-schedule/master/jayhawkschedule/static/images/team-page.png)
Team pages take further advantage of the ESPN API to include ESPN video, ESPN Team page links, latest ESPN articles, and team colors. Also uses the Twitter API for the latest tweets.
