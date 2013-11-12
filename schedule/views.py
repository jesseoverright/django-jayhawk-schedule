from django.shortcuts import render, get_object_or_404
from schedule.models import Game

def index(request):
    games = Game.objects.order_by('date')

    return render(request, 'schedule/index.html', {'games': games})


def game(request, slug):
    game = get_object_or_404(Game, slug=slug)

    game.get_espn_api_team_articles()

    return render(request, 'schedule/game.html', {
        'title': 'KU vs %s' % game.opponent,
        'game': game
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