from django.contrib import admin
from schedule.models import Game

class GameAdmin(admin.ModelAdmin):
    list_display = ['opponent', 'mascot','date','game_type']
    list_filter = ['date', 'game_type']
    search_fields = ['opponent', 'mascot']
    date_heirarchy = 'date'
    save_on_top = True
    prepopulated_fields = {'slug': ('opponent',)}

admin.site.register(Game, GameAdmin)