import random
import pybitflyer
import time
import json
from datetime import datetime
from trade.models import Trader, Position
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http.response import JsonResponse
from django.views.decorators.http import condition
from django.http import StreamingHttpResponse
from django.views.generic import UpdateView, DetailView, FormView, TemplateView, DeleteView
from django.utils.safestring import mark_safe
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_GET, require_POST

api = pybitflyer.API()


def index(request):
	return render(request, 'index.html')


@login_required
def trade(request):
	username = request.user
	trader = Trader.objects.get(username=username)
	cash = trader.cash
	token = trader.token
	print(request.body.decode())
	if request.method == "POST":
		str_body = request.body.decode()
		body_list = str_body.split("&")
		csrf_token = body_list[0]
		if csrf_token == token:
			token_bool = False
		else:
			token_bool = True
			change_token(username, csrf_token)
		
		btc_jpy_order = request.POST.get("btc_jpy_make_order")
		usd_jpy_order = request.POST.get("usd_jpy_make_order")
		nikkei_jpy_order = request.POST.get("nikkei_jpy_make_order")
		liquidation = request.POST.get("liquidation")
		print(liquidation)
		print(type(liquidation))
		
		if token_bool:
			if btc_jpy_order:
				amount = request.POST.get("btc_jpy_amount")
				dict = make_position(btc_jpy_order, amount, username)
			
			if usd_jpy_order:
				amount = request.POST.get("usd_jpy_amount")
				dict = make_position(usd_jpy_order, amount, username)
			
			if nikkei_jpy_order:
				amount = request.POST.get("nikkei_jpy_amount")
				dict = make_position(nikkei_jpy_order, amount, username)
			
			if liquidation:
				positions = Position.objects.filter(trader=username)
				for p in positions:
					server_liquidation = liquidation
					client_liquidation = p.pair + p.ls + str(p.amount) + str(p.price) + str(p.timestamp)
					if server_liquidation == client_liquidation:
						print("=============")
						print("Liquidation")
						liquidate(username, p.pair, p.ls, p.amount, p.price, p.timestamp)
		else:
			print("not token_bool")
	
	else:
		pass
	
	t = Trader.objects.get(username=username)
	positions = Position.objects.filter(trader=username)
	position_list = []
	for p in positions:
		pair = p.pair
		ls = p.ls
		amount = p.amount
		price = p.price
		order_date = datetime.fromtimestamp(int(p.timestamp)).strftime("%Y/%m/%d %H:%M:%S")
		timestamp = p.timestamp
		position_list.append([pair, ls, amount, price, order_date, timestamp])
	dict = {
		    "username":username,
		    "cash":t.cash,
		    "position_list":position_list
		}
	return render(request, "trade/trade.html", dict)


def liquidate(username, pair, ls, amount, price, timestamp):
	print("Liquidate")
	t = Trader.objects.get(username=username)
	t.cash += 1000
	t.save()
	Position.objects.get(pair=pair, ls=ls, amount=amount, price=price, trader=username, timestamp=timestamp).delete()


def make_position(make_order, new_amount, username):
	ticker = api.ticker(product_code="FX_BTC_JPY")
	if make_order == "買い":
		new_price = ticker["best_ask"]
		new_position = ["BTC/JPY", "Long", new_amount, new_price]
	else:
		new_price = ticker["best_bid"]
		new_position = ["BTC/JPY", "Short", new_amount, new_price]
	model_position = Position(
		pair = new_position[0],
		ls = new_position[1],
		amount = new_position[2],
		price = new_position[3],
		trader = username,
		timestamp = time.time()
	)
	model_position.save()


def change_token(username, csrf_token):
	t = Trader.objects.get(username=username)
	t.token = csrf_token
	t.save()


