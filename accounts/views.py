from trade.models import Trader
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect


def signup(request):
	if request.method == "POST":
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			trader = Trader(username=user)
			trader.save()
			login(request, user)
			return redirect("index")
	else:
		form = UserCreationForm()

	return render(request, "accounts/signup.html", {"form": form})

