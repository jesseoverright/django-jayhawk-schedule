from django.shortcuts import render, get_object_or_404
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

    for game in games:
        if game.get_result() == 'win' and game.game_type != 'Exhibition':
            record['wins'] += 1
        if game.get_result() == 'loss' and game.game_type != 'Exhibition':
            record['losses'] += 1

    return render(request, 'schedule/index.html', {'games': games, 'record': record, 'next_game': next_game})


def game(request, slug):
    game = get_object_or_404(Game, slug=slug)

    game.opponent.get_news()

    return render(request, 'schedule/game.html', {
        'title': 'KU vs %s' % game.opponent,
        'game': game
    })

def team(request, slug):
    team = get_object_or_404(Team, slug=slug)
    games = Game.objects.filter(opponent=team)

    team.get_news()

    return render(request, 'schedule/team.html', {
        'title': '%s Team Page' % team,
        'team': team,
        'games': games,
    })

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