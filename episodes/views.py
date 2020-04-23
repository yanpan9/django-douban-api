import re
import json 

from urllib import request
from django.http import HttpResponse
from bs4 import BeautifulSoup

def parse_episode(req):
	res = dict()
	with request.urlopen(req) as response:
		data = response.read()
		soup = BeautifulSoup(data)
		# Regular Expression can be used, too
		# and can do better
		ep_info = soup.find("ul", class_="ep-info")
		lst = ep_info.find_all("li")
		name = lst[0].find("span", class_="all")
		if name:
			res["name"] = name.string
		else:
			res["name"] = None
		name_ori = lst[1].find("span", class_="all")
		if name_ori:
			res["name_ori"] = name_ori.string
		else:
			res["name_ori"] = None
		if (not name) and name_ori:
			res["name"] = res["name_ori"]
		date =  lst[2].find("span", class_="all")
		if date:
			res["release_date"] = date.string
		else:
			res["release_date"] = None
		intro = lst[3].find("span", class_="all")
		if intro:
			if not intro.string:
				res["intro"] = intro.get_text()
			else:
				res["intro"] = intro.string
			hide = lst[3].find("span", class_="hide")
			if hide:
				string = hide.string
				if string:
					res["intro"] += hide.string
				else:
					res["intro"] += hide.get_text()
		else:
			res["intro"] = None
		return res

def get_episodes(douban_id, episodes_num):
	user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"
	headers = {"User-Agent":user_agent}

	infos = dict()
	for i in range(1, episodes_num+1):
		url = f"https://movie.douban.com/subject/{douban_id}/episode/{i}/"
		req = request.Request(url=url, headers=headers)
		infos[i] = parse_episode(req)
	return infos

def episodes(request):
	douban_id = request.GET.get("id")
	count = request.GET.get("episodes")
	try:
		count = int(count)
	except:
		return HttpResponse("Invalid episodes number.")
	infos = get_episodes(douban_id, count)
	response_str = json.dumps(infos)
	return HttpResponse(response_str)