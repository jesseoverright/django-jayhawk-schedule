from django.shortcuts import render, get_object_or_404, get_list_or_404
from schedule.models import Game, Team

from datetime import date

def index(request):
    games = Game.objects.order_by('date')

    next_games = Game.objects.filter(date__gt = date.today()).order_by('date')
    if next_games.count() > 0:
        if next_games[0].get_result() != False:
            next_game = next_games[1]
        else:
            next_game = next_games[0]
    else:
        next_game = False

    record = {}
    record['wins'] = 0
    record['losses'] = 0
    record['conference_wins'] = 0
    record['conference_losses'] = 0


    for game in games:
        if game.get_result() == 'win' and game.game_type != 'Exhibition':
            record['wins'] += 1
            if game.game_type == 'Conference':
                record['conference_wins'] += 1
        if game.get_result() == 'loss' and game.game_type != 'Exhibition':
            record['losses'] += 1
            if game.game_type == 'Conference':
                record['conference_losses'] += 1

    return render(request, 'schedule/index.html', {'games': games, 'record': record, 'next_game': next_game})

def all_teams(request):
    teams = Team.objects.order_by('name')

    return render(request, 'schedule/teams.html', {'teams': teams})

def game(request, slug):
    game = get_object_or_404(Game, slug=slug)
    team, created = Team.objects.get_or_create(slug='kansas-jayhawks')

    game.opponent.get_news(6)
    game.opponent.get_videos(2)
    game.opponent.get_podcasts(4)

    team.get_videos(1)

    return render(request, 'schedule/game.html', {
        'title': '%s vs %s' % (team, game.opponent),
        'game': game,
        'team': team,
        'videos': game.opponent.videos + team.videos,
    })

def team(request, slug):
    team = get_object_or_404(Team, slug=slug)
    games = Game.objects.filter(opponent=team).order_by('date')

    team.get_news(8)
    team.get_videos(3)
    team.get_podcasts(8)

    return render(request, 'schedule/team.html', {
        'title': '%s Team Page' % team,
        'team': team,
        'games': games,
    })

def category(request, slug):
    games = get_list_or_404(Game.objects.filter(game_type__iexact=slug).order_by('date'))

    return render(request, 'schedule/category.html', {'game_type': slug, 'games': games})

def ical(request):
    games = Game.objects.order_by('date')

    title = 'Kansas Jayhawks 2013-14 Schedule'

    response = render(request, 'schedule/ical.html', {
        'title': title,
        'games': games,
    })

    response['Content-type'] = 'text/calendar; charset=utf-8'
    response['Content-disposition'] = 'attachement; filename="'+title+'"'

    return response