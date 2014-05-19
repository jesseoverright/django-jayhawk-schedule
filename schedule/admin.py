from django.contrib import admin
from schedule.models import Team, Game

class GameAdmin(admin.ModelAdmin):
    list_display = ['opponent','date','location','game_type', 'season']
    list_filter = ['date', 'game_type']
    search_fields = ['location']
    ordering = ('-season', 'date',)
    save_on_top = True
    prepopulated_fields = {'slug': ('date',)}

class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'mascot', 'conference']
    search_fields = ['name', 'mascot','conference']
    ordering = ('name','mascot')
    save_on_top = True
    prepopulated_fields = {'slug': ('name','mascot')}

admin.site.register(Game, GameAdmin)
admin.site.register(Team, TeamAdmin)