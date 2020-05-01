import re
import json 

from urllib import request
from django.http import HttpResponse
from bs4 import BeautifulSoup

def parse_celebrity(celebrity):
	result = dict()
	a = celebrity.find("a")
	avatar = a.find("div", class_="avatar")["style"]
	result["photo"] = re.findall(r"url\((.+?)\)",avatar)[-1]

	info = celebrity.find("div", class_="info")
	name = info.find("span", class_="name").string
	if " " in name:
		result["name"], result["name_en"] = name.split(" ", maxsplit=1)
	else:
		result["name"] = name 
	role = info.find("span", class_="role").string
	if "(" in role:
		role = re.search(r"\(. (.+?)\)", role).group(1)
		result["role"] = role
	
	return result

def get_celebrities(douban_id):
	user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36"
	headers = {"User-Agent":user_agent}

	url = f"https://movie.douban.com/subject/{douban_id}/celebrities"
	req = request.Request(url=url, headers=headers)
	with request.urlopen(req) as response:
		data = response.read()
		soup = BeautifulSoup(data)
		wrapper = soup.find("div", id="wrapper")
		content = wrapper.find("div", id="content")
		grid = content.find("div", class_="grid-16-8 clearfix")
		article = grid.find("div", class_="article")
		celebrities = article.find("div", id="celebrities")
		lists = celebrities.find_all("div", class_="list-wrapper")
		head2str = {
			"导演 Director": "directors", 
			"演员 Cast": "casts",
			"编剧 Writer": "writers",
			#"制片人 Producer": "producers",
			#"音乐 Music Department": "musics",
			#"美术 Art Department": "arts",
			#"摄影 Camera Department": "cameras"
		}
		infos = dict()
		for element in lists:
			head = element.find("h2").string
			if head not in head2str:
				continue
			key = head2str[head]
			if key in infos:
				lst = infos[key]
			else:
				lst = list()
				infos[key] = lst
			for celebrity in element.find_all("li", class_="celebrity"):
				lst.append(parse_celebrity(celebrity))

		return infos

def celebrities(request):
	douban_id = request.GET.get("id")
	infos = get_celebrities(douban_id)
	response_str = json.dumps(infos)
	return HttpResponse(response_str)
