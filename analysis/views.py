from django.shortcuts import render
from django.http import HttpResponse


def analysis(request):
	return render(request, "analysis/analysis.html")

