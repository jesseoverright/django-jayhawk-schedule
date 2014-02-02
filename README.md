#Jayhawk Schedule

This is a simple django app built to track the __Kansas Jayhawks 2013-14__ basketball schedule.  The __Kansas Jayhawks 2013-14 Basketball Schedule__ provides all the latest news, videos, game recaps, tweets, stats and results of the Jayhawks season. You can view the project live at [http://jayhawkschedule.co](http://jayhawkschedule.co).

Main Features:

- utilizes the [ESPN API](http://developer.espn.com/docs) for video, team news, stats, game recaps, and details
- utilizes the [Twitter API](https://dev.twitter.com/docs/api/1.1/get/search/tweets) to display latest tweets about each team and game
- [Kenpom](http://kenpom.com) stats included for team ranking, offensive & defensive efficiency, and comparisions
- fully responsive design built with Compass & Sass
- generates an up to date ical calendar feed including results, location and tune in information
- gives admin ability to create games, set opponent, location, tv info
- update results as games occur

## Jayhawk Schedule Homepage
![Jayhawk Schedule Homepage](https://raw.github.com/jesseoverright/django-jayhawk-schedule/master/jayhawkschedule/static/images/home-page.png)
The homepage displays the full list of games, including results, location, television info and more at a glance.

## Game Pages
![Jayhawk Schedule Game Page](https://raw.github.com/jesseoverright/django-jayhawk-schedule/master/jayhawkschedule/static/images/game-page.png)
Game pages provide a snapshot of the upcoming opponent and provides matchup details with Kansas, including head-to-head comparisons of offensive and defensive efficiency from Kenpom. They take further advantage of the ESPN API to include ESPN video, ESPN Game page links, latest ESPN news, ESPN podcasts, and team colors. Game pages also uses the Twitter API for the latest tweets. After a game has been played, the ESPN game recap is displayed.

## Team Pages
![Jayhawk Schedule Team Page](https://raw.github.com/jesseoverright/django-jayhawk-schedule/master/jayhawkschedule/static/images/team-page.png)
Team pages are available for every KU opponent. They provide game details for upcoming games vs KU, team stats, ESPN video, links, articles and twitter timelines specific to individual teams.
