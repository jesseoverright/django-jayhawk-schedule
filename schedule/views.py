from django.shortcuts import render, get_object_or_404, get_list_or_404
from django.utils import timezone
from django.conf import settings
from django.views.decorators.cache import cache_page
from schedule.models import Game, Team

from datetime import date

@cache_page(settings.CACHE_TIMEOUT, cache='page_views')
def index(request):
    games = Game.objects.filter(season = settings.SCHEDULE_SETTINGS['year']).order_by('date')

    next_games = Game.objects.filter(date__gt = timezone.now(), season = settings.SCHEDULE_SETTINGS['year']).order_by('date')
    if next_games.count() > 0:
        if next_games[0].get_result() != False:
            if next_games.count() > 1:
                next_game = next_games[1]
            else:
                next_game = False
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

    return render(request, 'schedule/index.html', {
        'games': games,
        'record': record,
        'next_game': next_game,
        'schedule_settings': settings.SCHEDULE_SETTINGS,
    })

@cache_page(settings.CACHE_TIMEOUT, cache='page_views')
def all_teams(request):
    teams = Team.objects.order_by('name')

    return render(request, 'schedule/teams.html', {
        'teams': teams,
        'schedule_settings': settings.SCHEDULE_SETTINGS
    })

@cache_page(settings.CACHE_TIMEOUT, cache='page_views')
def game(request, season, slug):
    game = get_object_or_404(Game, season=season, slug=slug)

    if game.get_result() == 'win' or game.get_result() == 'loss':
        game.get_news(4)
    else:
        game.get_news(8)

    game.get_videos(2)
    game.get_podcasts(6)

    return render(request, 'schedule/game.html', {
        'title': '%s vs %s' % (game.team, game.opponent),
        'game': game,
        'schedule_settings': settings.SCHEDULE_SETTINGS,
    })

@cache_page(settings.CACHE_TIMEOUT, cache='page_views')
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
        'schedule_settings': settings.SCHEDULE_SETTINGS,
    })

@cache_page(settings.CACHE_TIMEOUT, cache='page_views')
def category(request, slug):
    games = get_list_or_404(Game.objects.filter(game_type__iexact=slug).order_by('date'))

    return render(request, 'schedule/category.html', {
        'game_type': slug,
        'games': games,
        'schedule_settings': settings.SCHEDULE_SETTINGS,
    })

@cache_page(settings.CACHE_TIMEOUT, cache='page_views')
def ical(request):
    games = Game.objects.order_by('date')
    schedule_settings = settings.SCHEDULE_SETTINGS

    title = '%s %s Schedule' % (schedule_settings['team']['name'], schedule_settings['year'])

    response = render(request, 'schedule/ical.html', {
        'title': title,
        'games': games,
        'schedule_settings': settings.SCHEDULE_SETTINGS,
    })

    response['Content-type'] = 'text/calendar; charset=utf-8'
    response['Content-disposition'] = 'attachement; filename="'+title+'"'

    return response