import json
import time
import threading
import pybitflyer
from datetime import datetime
from trade import views
from trade.models import Trader, Position
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from channels.generic.websocket import WebsocketConsumer


options = Options()
options.set_headless(True)
driver = webdriver.Chrome(chrome_options=options)

api = pybitflyer.API()

class ChatConsumer(WebsocketConsumer):
	
	def connect(self):
		self.stop_event = threading.Event()
		self.inc_event = threading.Event()
		self.thread = threading.Thread(target = self.target)
		self.thread.start()
		self.accept()

	def disconnect(self, close_code):
		self.stop()

	def receive(self, text_data):
		text_data_json = json.loads(text_data)
		if "open" in text_data_json.keys():
			username = text_data_json["open"]
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
			
			self.send(text_data=json.dumps({
				"cash":t.cash,
				"position_list":position_list
			}))
		if "liquidation" in text_data_json.keys():
			print("liquidation")
			username = text_data_json["username"]
			pair = text_data_json["pair"]
			ls = text_data_json["ls"]
			amount = text_data_json["amount"]
			price = text_data_json["price"]
			timestamp = text_data_json["timestamp"]
			t = Trader.objects.get(username=username)
			t.cash += 1000
			t.save()
			Position.objects.get(pair=pair, ls=ls, amount=amount, price=price, trader=username, timestamp=timestamp).delete()
			
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
			#self.send(text_data=json.dumps({
			#	"position_list":position_list
			#}))

	def target(self):
		while not self.stop_event.is_set():
			try:
				driver.get("https://nikkei225jp.com/chart/")
				html = driver.page_source.encode('utf-8')
				soup = BeautifulSoup(html, "html.parser")
				nikkei_jpy_soup = str(soup.select("#V111")[0])
				usd_jpy_soup = str(soup.select("#V511")[0])
				nikkei_jpy = int(float(nikkei_jpy_soup.split("</p>")[0].split(">")[-1].replace(",", "")))
				usd_jpy = float(usd_jpy_soup.split("</p>")[0].split(">")[-1])
				btc_jpy = api.ticker(product_code="BTC_JPY")
				self.send(text_data=json.dumps({
					"nikkei_jpy_best_bid":nikkei_jpy-1,
					"nikkei_jpy_best_ask":nikkei_jpy+1,
					"usd_jpy_best_bid":usd_jpy-0.01,
					"usd_jpy_best_ask":usd_jpy+0.01,
					"btc_jpy_best_bid":btc_jpy["best_bid"],
					"btc_jpy_best_ask":btc_jpy["best_ask"]
				}))
				time.sleep(1)
			except Exception as e:
				print(e)

	def stop(self):
		self.stop_event.set()
		self.thread.join()


