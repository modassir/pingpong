from django.db import models


class Players(models.Model):
	uid = models.ForeignKey('auth.User', related_name='player')
	name = models.CharField(max_length=50)
	defence_len = models.IntegerField()
	joined = models.IntegerField(default=0)
	tour_status = models.IntegerField(default=0)
	round1_gameid = models.IntegerField(null=True)
	round1_qualified = models.IntegerField(null=True)
	round2_gameid = models.IntegerField(null=True)
	round2_qualified = models.IntegerField(null=True)
	round3_gameid = models.IntegerField(null=True)
	round3_winner = models.IntegerField(null=True)

class Game(models.Model):
	player1_id = models.IntegerField(null=True)
	player2_id = models.IntegerField(null=True)
	player1_responses = models.CharField(max_length=200)
	player2_responses = models.CharField(max_length=200)
	start_time = models.DateTimeField()
	end_time = models.DateTimeField(null=True)
	player1_score = models.IntegerField(default=0)
	player2_score = models.IntegerField(default=0)
	order = models.IntegerField()
	round_no = models.IntegerField()

class Variables(models.Model):
	count = models.IntegerField(default=1)
	x = models.CharField(max_length=50, default="[1,2,3,4,5,6,7,8]")