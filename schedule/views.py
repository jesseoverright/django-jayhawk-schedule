from django.shortcuts import render, get_object_or_404
from schedule.models import Game

def index(request):
    games = Game.objects.order_by('date')

    return render(request, 'schedule/index.html', {'games': games})


def game(request, slug):
    game = get_object_or_404(Game, slug=slug)

    return render(request, 'schedule/game.html', {
        'title': 'KU vs %s' % game.opponent,
        'game': game
    })