from django.contrib import admin
from schedule.models import Team, Game

class GameAdmin(admin.ModelAdmin):
    list_display = ['opponent','date','location','game_type']
    list_filter = ['date', 'game_type']
    search_fields = ['location']
    date_heirarchy = 'date'
    save_on_top = True
    prepopulated_fields = {'slug': ('date',)}
    
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'mascot']
    search_fileds = ['name', 'mascot']
    save_on_top = True
    prepopulated_fields = {'slug': ('name','mascot')}

admin.site.register(Game, GameAdmin)
admin.site.register(Team, TeamAdmin)