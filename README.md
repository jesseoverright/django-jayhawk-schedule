#Jayhawk Schedule

This is a simple django app built to track the __Kansas Jayhawks 2013-14__ basketball schedule.  The __Kansas Jayhawks 2013-14 Basketball Schedule__ provides all the latest news and results for the Jayhawks season. It's rebuilt from the group up based on the original [codeigniter project](https://github.com/jesseoverright/jayhawk-schedule/).

Main Features:

- gives admin ability to create games, set opponent, location, tv info
- takes advantage of the [ESPN API](http://developer.espn.com/docs) for video, team news, stats, and details
- generates a ical calendar feed
- update results as games occur

## Jayhawk Schedule Homepage
![Jayhawk Schedule Homepage](https://raw.github.com/jesseoverright/django-jayhawk-schedule/master/jayhawkschedule/static/images/home-page.png)
The homepage displays the full list of games, including results, upcoming games, location, television info and more at a glance.

## Team Pages
![Jayhawk Schedule Team Page](https://raw.github.com/jesseoverright/django-jayhawk-schedule/master/jayhawkschedule/static/images/team-page.png)
Team pages take further advantage of the ESPN API to include ESPN video, ESPN Team page links, latest ESPN articles, and team colors.
