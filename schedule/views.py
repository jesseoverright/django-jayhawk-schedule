from django.shortcuts import render, get_object_or_404
from schedule.models import Game

def index(request):
    # get games
    games = Game.objects.filter(published=True)

    return render(request, 'schedule/index.html', {'games': games})


def game(request, slug):
    game = get_object_or_404(Game, slug=slug)

    return render(request, 'schedule/game.html', {'game': game})