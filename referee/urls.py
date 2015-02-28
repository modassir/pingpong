from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from referee import views

urlpatterns = [
    url(r'^join/', views.join_game, name="join"),
    url(r'^join/status/', views.join_status, name="join_status"),
    url(r'^game/details/1/', views.game_details, name="game_details"),
    url(r'^game/details/2/', views.game_details2, name="game_details2"),
    url(r'^game/details/3/', views.game_details3, name="game_details3"),
    url(r'^game/round/1/', views.start_round1, name="round1"),
    url(r'^game/round/2/', views.start_round2, name="round2"),
    url(r'^game/round/3/', views.start_round3, name="round3"),
    url(r'^game/status/1/', views.game_status, name="status1"),
    url(r'^game/status/2/', views.game_status2, name="status2"),
    url(r'^game/status/3/', views.game_status3, name="status3"),
    url(r'^game/report/', views.game_report, name="report"),
]

#urlpatterns = format_suffix_patterns(urlpatterns)