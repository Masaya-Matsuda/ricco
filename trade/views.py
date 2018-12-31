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
	btc_jpy_ticker = api.ticker(product_code="BTC_JPY")
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
		btc_jpy_ticker = api.ticker(product_code="BTC_JPY")
		make_order = request.POST.get("btc_jpy_make_order")
		liquidation = request.POST.get("liquidation")
		print(liquidation)
		print(type(liquidation))
		
		if token_bool:
			if make_order:
				new_amount = round(random.random(), 3)
				dict = make_position(make_order, new_amount, username)
			
			if liquidation:
				positions = Position.objects.filter(trader=username)
				for p in positions:
					server_liquidation = liquidation
					client_liquidation = p.pair + p.ls + str(p.amount) + str(p.price) + str(p.order_date)
					if server_liquidation == client_liquidation:
						print("=============")
						print("Liquidation")
						liquidate(username, p.pair, p.ls, p.amount, p.price, p.order_date)
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
		order_date = datetime.fromtimestamp(int(p.order_date)).strftime("%Y/%m/%d %H:%M:%S")
		timestamp = p.order_date
		position_list.append([pair, ls, amount, price, order_date, timestamp])
	dict = {
	        "btc_jpy_best_bid":btc_jpy_ticker["best_bid"],
	        "btc_jpy_best_ask":btc_jpy_ticker["best_ask"],
		    "username":username,
		    "cash":t.cash,
		    "position_list":position_list
		}
	return render(request, "trade/trade.html", dict)


def liquidate(username, pair, ls, amount, price, order_date):
	print("Liquidate")
	t = Trader.objects.get(username=username)
	t.cash += 1000
	t.save()
	Position.objects.get(pair=pair, ls=ls, amount=amount, price=price, trader=username, order_date=order_date).delete()


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
		order_date = time.time()
	)
	model_position.save()


def change_token(username, csrf_token):
	t = Trader.objects.get(username=username)
	t.token = csrf_token
	t.save()


