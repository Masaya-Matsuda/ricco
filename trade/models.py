from django.db import models


class Trader(models.Model):
	username = models.CharField(max_length=1000)
	cash = models.FloatField(default=1000000)
	token = token = models.CharField(max_length=1000)
	
	def __str__(self):
		return "username:" + self.username + " / cash:" + str(self.cash) + " / token:" + self.token


class Position(models.Model):
	pair = models.CharField(max_length=100)
	ls = models.CharField(max_length=100)
	amount = models.FloatField()
	price = models.FloatField()
	trader = models.CharField(max_length=1000)
	order_date = models.FloatField()
	
	def __str__(self):
		return self.pair + self.ls + str(self.amount) + str(self.price) + str(self.trader) + str(self.order_date)


