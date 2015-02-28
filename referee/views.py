from django.http import Http404
from django.http import HttpResponseRedirect,HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from referee.models import Players
from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
import random
from referee.models import Game
from django.utils import timezone
from django.db.models import Q
from referee.models import Variables


@api_view(['GET',])
def join_game(request):
	if request.method=="GET":
		User = request.user
		Player_obj = Players.objects.filter(uid=User.id)
		try:
			Player_obj.update(joined=1)
			content = {"Joined":"True"}
		except:
			content = {"Joined":"False"}
		joined_players = Players.objects.filter(joined=1)
		joined_players_no = len(joined_players)
		if(joined_players_no == 8):
			Var_id = Variables.objects.filter(id=1)
			count = Var_id[0].count
			x = (Var_id[0].x).replace('[','').replace(']','').split(',')
			if(Var_id[0].x == '[]'):
				content = {"Status":"All Players Joined!"}
				return Response(content)
			x = map(int, x)
			while(len(x)!=0):
				random.shuffle(x)
				p1_i = x.pop
				p2_i = x.pop
				p1 = Players.objects.filter(id=p1_i)
				p2 = Players.objects.filter(id=p2_i)
				Game(player1_id=int(p1[0].id),player2_id=int(p2[0].id),start_time=timezone.now(),round_no=1,order=1).save()
				Players.objects.filter(Q(uid=p1[0].uid) | Q(uid=p2[0].uid)).update(round1_gameid=count)
				count = count +1
				Variables.objects.filter(id=1).update(count=count,x=str(x))
		return Response(content)
	return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET',])
def join_status(request):
	if request.method=="GET":
		User = request.user
		Player_obj = Players.objects.filter(uid=User.id)[0]
		if(Player_obj.joined==1):
			joined =  "True"
		else:
			joined = "False"
		content = {"Joined":joined}
		joined_players_no = len(Players.objects.filter(joined=1))
		content["No. of Players joined"] = joined_players_no
		return Response(content)
	return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET',])
def game_details(request):
	if request.method=="GET":
		User = request.user
		Player_obj = Players.objects.filter(uid=User.id)[0]
		game_id = Player_obj.round1_gameid
		opp_id = Players.objects.filter(round1_gameid=game_id).exclude(uid=User.id)[0]
		opp = opp_id.name
		if(Player_obj.id == Game.objects.filter(id=game_id)[0].player1_id):
			order = "1st"
		else:
			order = "2nd"
		def_len = Player_obj.defence_len
		content = {"Game ID":game_id,"Round":1,"Opponent Name":opp,"Order of Playing":order,"Defence Array Length":def_len}
		return Response(content)

@api_view(['GET','POST'])
def start_round1(request):
	if request.method == "POST":
		User = request.user
		Player_obj = Players.objects.filter(uid=User.id)[0]
		p_id = Player_obj.id
		game_id = Player_obj.round1_gameid
		opp_obj = Players.objects.filter(round1_gameid=game_id).exclude(uid=User.id)[0]
		shot = str(request.POST['input'])
		Game_obj = Game.objects.filter(id=game_id)[0]
		p1_response = (Game_obj.player1_responses).split("+")
		p2_response = (Game_obj.player2_responses).split("+")
		if (abs(len(p1_response)-len(p2_response)) <= 1 and Game_obj.player1_score != 5 and Game_obj.player2_score != 5):
			if(p_id == Game_obj.player1_id):
				if(Game_obj.player1_responses == ''):
					shot = shot
				else:
					shot = shot + "+" + Game_obj.player1_responses
					if(abs(len(p2_response)-len(shot.split("+"))) > 1):
						return Response({"Status":"Opponent's turn"})
				Game.objects.filter(id=game_id).update(player1_responses=shot)
			else:
				if(Game_obj.player2_responses == ''):
					shot = shot
				else:
					shot = shot + "+" + Game_obj.player2_responses
					if(abs(len(p1_response)-len(shot.split("+"))) > 1):
						return Response({"Status":"Opponent's turn"})
				Game.objects.filter(id=game_id).update(player2_responses=shot)
		else:
			return Response({"Status":"Opponent's turn"})
		Game_obj = Game.objects.filter(id=game_id)[0]
		p1_response = (Game_obj.player1_responses).split("+")
		p2_response = (Game_obj.player2_responses).split("+")
		if (len(p1_response) == len(p2_response) and (p1_response != ['']) and (p2_response != ['']) and Game_obj.player1_score != 5 and Game_obj.player2_score != 5):
			Game_obj = Game.objects.filter(id=game_id)[0]
			if(Game_obj.order == 1):
				p1_rval = int((Game_obj.player1_responses).split("+")[0])
				p2_rval = (Game_obj.player2_responses).split("+")[0].replace('[','').replace(']','').split(',')
				p2_rval = map(int, p2_rval)
				len_arr = Players.objects.filter(id=Game_obj.player2_id)[0].defence_len
				counter = 0
				for i in range(0,len_arr):
					if(p1_rval == p2_rval[i]):
						counter = 1
				if(counter==1):
					score = Game_obj.player2_score
					score = score + 1
					Game.objects.filter(id=game_id).update(player2_score=score,order=2)
				else:
					score = Game_obj.player1_score
					score = score + 1
					Game.objects.filter(id=game_id).update(player1_score=score,order=1)
			else:
				p2_rval = int((Game_obj.player2_responses).split("+")[0])
				p1_rval = (Game_obj.player1_responses).split("+")[0].replace('[','').replace(']','').split(',')
				p1_rval = map(int, p1_rval)
				len_arr = Players.objects.filter(id=Game_obj.player1_id)[0].defence_len
				counter = 0
				for i in range(0,len_arr):
					if(p2_rval == p1_rval[i]):
						counter = 1
				if(counter==1):
					score = Game_obj.player1_score
					score = score + 1
					Game.objects.filter(id=game_id).update(player1_score=score,order=1)
				else:
					score = Game_obj.player2_score
					score = score + 1
					Game.objects.filter(id=game_id).update(player2_score=score,order=2)

		Game_obj = Game.objects.filter(id=game_id)[0]
		if(Game_obj.player1_score == 5):
			Players.objects.filter(id=Game_obj.player1_id).update(round1_qualified=1)
			Players.objects.filter(id=Game_obj.player2_id).update(round1_qualified=0,tour_status=1)
			Game.objects.filter(id=game_id).update(end_time=timezone.now())
			x = (Variables.objects.filter(id=1)[0].x).replace('[','').replace(']','').split(',')
			if(x==['']):
				x[0] = '1'
				x = map(int, x)
				del x[0]
			else:
				x = map(int, x)
			x.append(int(Game_obj.player1_id))
			Variables.objects.filter(id=1).update(x=x)
		elif(Game_obj.player2_score == 5):
			Players.objects.filter(id=Game_obj.player1_id).update(round1_qualified=0,tour_status=1)
			Players.objects.filter(id=Game_obj.player2_id).update(round1_qualified=1)
			Game.objects.filter(id=game_id).update(end_time=timezone.now())
			x = (Variables.objects.filter(id=1)[0].x).replace('[','').replace(']','').split(',')
			if(x==['']):
				x[0] = '1'
				x = map(int, x)
				del x[0]
			else:
				x = map(int, x)
			x.append(int(Game_obj.player2_id))
			Variables.objects.filter(id=1).update(x=x)
		x = (Variables.objects.filter(id=1)[0].x).replace('[','').replace(']','').split(',')
		if(x==['']):
			x[0] = '1'
			x = map(int, x)
			del x[0]
		else:
			x = map(int, x)
		if(len(x) == 4):
			while(len(x)!=0):
				random.shuffle(x)
				p1_i = x.pop
				p2_i = x.pop
				p1 = Players.objects.filter(id=p1_i)
				p2 = Players.objects.filter(id=p2_i)
				Var_id = Variables.objects.filter(id=1)
				count = Var_id[0].count
				Game(player1_id=int(p1[0].id),player2_id=int(p2[0].id),start_time=timezone.now(),round_no=2,order=1).save()
				Players.objects.filter(Q(uid=p1[0].uid) | Q(uid=p2[0].uid)).update(round2_gameid=count)
				count = count + 1
				Variables.objects.filter(id=1).update(count=count,x=str(x))
		return Response(shot)

	return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET',])
def game_status(request):
	if request.method=="GET":
		User = request.user
		Player_obj = Players.objects.filter(uid=User.id)[0]
		game_id = Player_obj.round1_gameid
		Game_obj = Game.objects.filter(id=game_id)[0]
		if(Player_obj.id == Game_obj.player1_id):
			content = {"Your Score":Game_obj.player1_score}
			content["Opponent Score"] = Game_obj.player2_score
			if(Game_obj.player1_score != 5 and Game_obj.player2_score != 5):
				if(Game_obj.order == 1):
					msg = "1st"
				else:
					msg = "2nd" 
				content["New Order"] = msg
			content["Round"] = Game_obj.round_no
			if(Game_obj.player1_score == 5):
				content["Qualified"] = "Yes"
			elif(Game_obj.player2_score == 5):
				content["Qualified"] = "No"
		else:
			content = {"Your Score":Game_obj.player2_score}
			content["Opponent Score"] = Game_obj.player1_score
			if(Game_obj.player1_score != 5 and Game_obj.player2_score != 5):
				if(Game_obj.order == 2):
					msg = "1st"
				else:
					msg = "2nd" 
				content["New Order"] = msg
			content["Round"] = Game_obj.round_no
			if(Game_obj.player2_score == 5):
				content["Qualified"] = "Yes"
			elif(Game_obj.player1_score == 5):
				content["Qualified"] = "No"
		return Response(content)
	return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET','POST'])
def start_round2(request):
	if request.method=="POST":
		User = request.user
		Player_obj = Players.objects.filter(uid=User.id)
		if(Player_obj[0].round1_qualified == 0):
			return Response({"Status":"Not Qualified"})
		elif(Player_obj[0].round1_qualified == 1):
			p_id = Player_obj[0].id
			game_id = Player_obj[0].round2_gameid
			opp_obj = Players.objects.filter(round2_gameid=game_id).exclude(uid=User.id)[0]
			shot = str(request.POST['input'])
			Game_obj = Game.objects.filter(id=game_id)[0]
			p1_response = (Game_obj.player1_responses).split("+")
			p2_response = (Game_obj.player2_responses).split("+")
			if (abs(len(p1_response)-len(p2_response)) <= 1 and Game_obj.player1_score != 5 and Game_obj.player2_score != 5):
				if(p_id == Game_obj.player1_id):
					if(Game_obj.player1_responses == ''):
						shot = shot
					else:
						shot = shot + "+" + Game_obj.player1_responses
						if(abs(len(p2_response)-len(shot.split("+"))) > 1):
							return Response({"Status":"Opponent's turn"})
					Game.objects.filter(id=game_id).update(player1_responses=shot)
				else:
					if(Game_obj.player2_responses == ''):
						shot = shot
					else:
						shot = shot + "+" + Game_obj.player2_responses
						if(abs(len(p1_response)-len(shot.split("+"))) > 1):
							return Response({"Status":"Opponent's turn"})
					Game.objects.filter(id=game_id).update(player2_responses=shot)
			else:
				return Response({"Status":"Opponent's turn"})
			Game_obj = Game.objects.filter(id=game_id)[0]
			p1_response = (Game_obj.player1_responses).split("+")
			p2_response = (Game_obj.player2_responses).split("+")
			if (len(p1_response) == len(p2_response) and (p1_response != ['']) and (p2_response != ['']) and Game_obj.player1_score != 5 and Game_obj.player2_score != 5):
				Game_obj = Game.objects.filter(id=game_id)[0]
				if(Game_obj.order == 1):
					p1_rval = int((Game_obj.player1_responses).split("+")[0])
					p2_rval = (Game_obj.player2_responses).split("+")[0].replace('[','').replace(']','').split(',')
					p2_rval = map(int, p2_rval)
					len_arr = Players.objects.filter(id=Game_obj.player2_id)[0].defence_len
					counter = 0
					for i in range(0,len_arr):
						if(p1_rval == p2_rval[i]):
							counter = 1
					if(counter==1):
						score = Game_obj.player2_score
						score = score + 1
						Game.objects.filter(id=game_id).update(player2_score=score,order=2)
					else:
						score = Game_obj.player1_score
						score = score + 1
						Game.objects.filter(id=game_id).update(player1_score=score,order=1)
				else:
					p2_rval = int((Game_obj.player2_responses).split("+")[0])
					p1_rval = (Game_obj.player1_responses).split("+")[0].replace('[','').replace(']','').split(',')
					p1_rval = map(int, p1_rval)
					len_arr = Players.objects.filter(id=Game_obj.player1_id)[0].defence_len
					counter = 0
					for i in range(0,len_arr):
						if(p2_rval == p1_rval[i]):
							counter = 1
					if(counter==1):
						score = Game_obj.player1_score
						score = score + 1
						Game.objects.filter(id=game_id).update(player1_score=score,order=1)
					else:
						score = Game_obj.player2_score
						score = score + 1
						Game.objects.filter(id=game_id).update(player2_score=score,order=2)

			Game_obj = Game.objects.filter(id=game_id)[0]
			if(Game_obj.player1_score == 5):
				Players.objects.filter(id=Game_obj.player1_id).update(round2_qualified=1)
				Players.objects.filter(id=Game_obj.player2_id).update(round2_qualified=0,tour_status=1)
				Game.objects.filter(id=game_id).update(end_time=timezone.now())
				x = (Variables.objects.filter(id=1)[0].x).replace('[','').replace(']','').split(',')
				if(x==['']):
					x[0] = '1'
					x = map(int, x)
					del x[0]
				else:
					x = map(int, x)
				x.append(int(Game_obj.player1_id))
				Variables.objects.filter(id=1).update(x=x)
			elif(Game_obj.player2_score == 5):
				Players.objects.filter(id=Game_obj.player1_id).update(round2_qualified=0,tour_status=1)
				Players.objects.filter(id=Game_obj.player2_id).update(round2_qualified=1)
				Game.objects.filter(id=game_id).update(end_time=timezone.now())
				x = (Variables.objects.filter(id=1)[0].x).replace('[','').replace(']','').split(',')
				if(x==['']):
					x[0] = '1'
					x = map(int, x)
					del x[0]
				else:
					x = map(int, x)
				x.append(int(Game_obj.player2_id))
				Variables.objects.filter(id=1).update(x=x)
			x = (Variables.objects.filter(id=1)[0].x).replace('[','').replace(']','').split(',')
			if(x==['']):
				x[0] = '1'
				x = map(int, x)
				del x[0]
			else:
				x = map(int, x)
			if(len(x) == 2):
				while(len(x)!=0):
					random.shuffle(x)
					p1_i = x.pop
					p2_i = x.pop
					p1 = Players.objects.filter(id=p1_i)
					p2 = Players.objects.filter(id=p2_i)
					Var_id = Variables.objects.filter(id=1)
					count = Var_id[0].count
					Game(player1_id=int(p1[0].id),player2_id=int(p2[0].id),start_time=timezone.now(),round_no=3,order=1).save()
					Players.objects.filter(Q(uid=p1[0].uid) | Q(uid=p2[0].uid)).update(round3_gameid=count)
					count = count + 1
					Variables.objects.filter(id=1).update(count=count,x=str(x))
			return Response(shot)
		else:
			return Response(status=status.HTTP_204_NO_CONTENT)
	else:
		return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET',])
def game_status2(request):
	if request.method=="GET":
		User = request.user
		Player_obj = Players.objects.filter(uid=User.id)[0]
		game_id = Player_obj.round2_gameid
		Game_obj = Game.objects.filter(id=game_id)[0]
		if(Player_obj.id == Game_obj.player1_id):
			content = {"Your Score":Game_obj.player1_score}
			content["Opponent Score"] = Game_obj.player2_score
			if(Game_obj.player1_score != 5 and Game_obj.player2_score != 5):
				if(Game_obj.order == 1):
					msg = "1st"
				else:
					msg = "2nd" 
				content["New Order"] = msg
			content["Round"] = Game_obj.round_no
			if(Game_obj.player1_score == 5):
				content["Qualified"] = "Yes"
			elif(Game_obj.player2_score == 5):
				content["Qualified"] = "No"
		else:
			content = {"Your Score":Game_obj.player2_score}
			content["Opponent Score"] = Game_obj.player1_score
			if(Game_obj.player1_score != 5 and Game_obj.player2_score != 5):
				if(Game_obj.order == 2):
					msg = "1st"
				else:
					msg = "2nd" 
				content["New Order"] = msg
			content["Round"] = Game_obj.round_no
			if(Game_obj.player2_score == 5):
				content["Qualified"] = "Yes"
			elif(Game_obj.player1_score == 5):
				content["Qualified"] = "No"
		return Response(content)
	return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET',])
def game_details2(request):
	if request.method=="GET":
		User = request.user
		Player_obj = Players.objects.filter(uid=User.id)
		if(Player_obj[0].round1_qualified == 1):
			game_id = Player_obj[0].round2_gameid
			# print game_id
			opp_id = Players.objects.filter(round2_gameid=game_id).exclude(uid=User.id)
			opp = opp_id[0].name
			# print opp
			if(Player_obj[0].id == Game.objects.filter(id=game_id)[0].player1_id):
				order = "1st"
			else:
				order = "2nd"
			def_len = Player_obj[0].defence_len
			content = {"Game ID":game_id,"Round":2,"Opponent Name":opp,"Order of Playing":order,"Defence Array Length":def_len}
			return Response(content)
		else:
			return Response({"Status":"Not Qualified"})
	else:
		return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET','POST'])
def start_round3(request):
	if request.method=="POST":
		User = request.user
		Player_obj = Players.objects.filter(uid=User.id)
		Game_obj = Game.objects.filter(id=7)[0]
		if(Player_obj[0].round3_gameid == 7):
			p_id = Player_obj[0].id
			game_id = Player_obj[0].round3_gameid
			opp_obj = Players.objects.filter(round3_gameid=game_id).exclude(uid=User.id)[0]
			shot = str(request.POST['input'])
			Game_obj = Game.objects.filter(id=game_id)[0]
			p1_response = (Game_obj.player1_responses).split("+")
			p2_response = (Game_obj.player2_responses).split("+")
			if (abs(len(p1_response)-len(p2_response)) <= 1 and Game_obj.player1_score != 5 and Game_obj.player2_score != 5):
				if(p_id == Game_obj.player1_id):
					if(Game_obj.player1_responses == ''):
						shot = shot
					else:
						shot = shot + "+" + Game_obj.player1_responses
						if(abs(len(p2_response)-len(shot.split("+"))) > 1):
							return Response({"Status":"Opponent's turn"})
					Game.objects.filter(id=game_id).update(player1_responses=shot)
				else:
					if(Game_obj.player2_responses == ''):
						shot = shot
					else:
						shot = shot + "+" + Game_obj.player2_responses
						if(abs(len(p1_response)-len(shot.split("+"))) > 1):
							return Response({"Status":"Opponent's turn"})
					Game.objects.filter(id=game_id).update(player2_responses=shot)
			else:
				return Response({"Status":"Opponent's turn"})
			Game_obj = Game.objects.filter(id=game_id)[0]
			p1_response = (Game_obj.player1_responses).split("+")
			p2_response = (Game_obj.player2_responses).split("+")
			if (len(p1_response) == len(p2_response) and (p1_response != ['']) and (p2_response != ['']) and Game_obj.player1_score != 5 and Game_obj.player2_score != 5):
				Game_obj = Game.objects.filter(id=game_id)[0]
				if(Game_obj.order == 1):
					p1_rval = int((Game_obj.player1_responses).split("+")[0])
					p2_rval = (Game_obj.player2_responses).split("+")[0].replace('[','').replace(']','').split(',')
					p2_rval = map(int, p2_rval)
					len_arr = Players.objects.filter(id=Game_obj.player2_id)[0].defence_len
					counter = 0
					for i in range(0,len_arr):
						if(p1_rval == p2_rval[i]):
							counter = 1
					if(counter==1):
						score = Game_obj.player2_score
						score = score + 1
						Game.objects.filter(id=game_id).update(player2_score=score,order=2)
					else:
						score = Game_obj.player1_score
						score = score + 1
						Game.objects.filter(id=game_id).update(player1_score=score,order=1)
				else:
					p2_rval = int((Game_obj.player2_responses).split("+")[0])
					p1_rval = (Game_obj.player1_responses).split("+")[0].replace('[','').replace(']','').split(',')
					p1_rval = map(int, p1_rval)
					len_arr = Players.objects.filter(id=Game_obj.player1_id)[0].defence_len
					counter = 0
					for i in range(0,len_arr):
						if(p2_rval == p1_rval[i]):
							counter = 1
					if(counter==1):
						score = Game_obj.player1_score
						score = score + 1
						Game.objects.filter(id=game_id).update(player1_score=score,order=1)
					else:
						score = Game_obj.player2_score
						score = score + 1
						Game.objects.filter(id=game_id).update(player2_score=score,order=2)

			Game_obj = Game.objects.filter(id=game_id)[0]
			if(Game_obj.player1_score == 5):
				Players.objects.filter(id=Game_obj.player1_id).update(round3_winner=1)
				Players.objects.filter(id=Game_obj.player2_id).update(round3_winner=0,tour_status=1)
				Game.objects.filter(id=game_id).update(end_time=timezone.now())
			elif(Game_obj.player2_score == 5):
				Players.objects.filter(id=Game_obj.player1_id).update(round3_winner=0,tour_status=1)
				Players.objects.filter(id=Game_obj.player2_id).update(round3_winner=1)
				Game.objects.filter(id=game_id).update(end_time=timezone.now())
			return Response(shot)
		else:
			return Response({"Status":"Not Qualified"})
	else:
		return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET',])
def game_details3(request):
	if request.method=="GET":
		User = request.user
		Player_obj = Players.objects.filter(uid=User.id)
		if(Player_obj[0].round2_qualified == 1):
			game_id = Player_obj[0].round3_gameid
			#print game_id
			opp_id = Players.objects.filter(round3_gameid=game_id).exclude(uid=User.id)
			opp = opp_id[0].name
			# print opp
			if(Player_obj[0].id == Game.objects.filter(id=game_id)[0].player1_id):
				order = "1st"
			else:
				order = "2nd"
			def_len = Player_obj[0].defence_len
			content = {"Game ID":game_id,"Round":3,"Opponent Name":opp,"Order of Playing":order,"Defence Array Length":def_len}
			return Response(content)
		else:
			return Response({"Status":"Not Qualified"})
	else:
		return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET',])
def game_status3(request):
	if request.method=="GET":
		User = request.user
		Player_obj = Players.objects.filter(uid=User.id)[0]
		game_id = Player_obj.round3_gameid
		Game_obj = Game.objects.filter(id=game_id)[0]
		if(Player_obj.id == Game_obj.player1_id):
			content = {"Your Score":Game_obj.player1_score}
			content["Opponent Score"] = Game_obj.player2_score
			if(Game_obj.player1_score != 5 and Game_obj.player2_score != 5):
				if(Game_obj.order == 1):
					msg = "1st"
				else:
					msg = "2nd" 
				content["New Order"] = msg
			content["Round"] = Game_obj.round_no
			if(Game_obj.player1_score == 5):
				content["Winner"] = "Yes"
			elif(Game_obj.player2_score == 5):
				content["Winner"] = "No"
		else:
			content = {"Your Score":Game_obj.player2_score}
			content["Opponent Score"] = Game_obj.player1_score
			if(Game_obj.player1_score != 5 and Game_obj.player2_score != 5):
				if(Game_obj.order == 2):
					msg = "1st"
				else:
					msg = "2nd" 
				content["New Order"] = msg
			content["Round"] = Game_obj.round_no
			if(Game_obj.player2_score == 5):
				content["Winner"] = "Yes"
			elif(Game_obj.player1_score == 5):
				content["Winner"] = "No"
		return Response(content)
	return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET',])
def game_report(request):
	if request.method=="GET":
		User = request.user
		Player_obj = Players.objects.filter(uid=User.id)[0]
		content = []
		if(Player_obj.joined == 1):
			for i in range(1,8):
				Game_obj = Game.objects.filter(id=i)[0]
				pl1_name = Players.objects.filter(id=Game_obj.player1_id)[0].name
				pl2_name = Players.objects.filter(id=Game_obj.player2_id)[0].name
				p1_pt = Game_obj.player1_score
				p2_pt = Game_obj.player2_score
				content.append("Game ID"+str(i))
				content.append("Player1: "+pl1_name)
				content.append("Player1 Point: "+str(p1_pt))
				content.append("Player2: "+pl2_name)
				content.append("Player2 Point: "+str(p2_pt))
			if(Game.objects.filter(id=7)[0].player1_score == 5):
				name = Players.objects.filter(id=Game.objects.filter(id=7)[0].player1_id)[0].name
			elif(Game.objects.filter(id=7)[0].player2_score == 5):
				name = Players.objects.filter(id=Game.objects.filter(id=7)[0].player2_id)[0].name
			content.append("Tornament Winner: "+name)
			return Response(content)
		else:
			return Response({"Status":"UnAuthenticated"})
	return Response(status=status.HTTP_204_NO_CONTENT)