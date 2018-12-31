import json
import time
import threading
import pybitflyer
from trade import views
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
		message = text_data_json["message"]
		self.send(text_data=json.dumps({
			"message": message
		}))
	
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


