from flask import Flask
import httpx
from bs4 import BeautifulSoup as bs
from deta import Deta, App
# from deta import Deta
import time

app = App(Flask(__name__))
# app = Flask(__name__)
url = 'https://javdb.com'
# deta_key = 'c0hs7k4a_B6nWnRF7wzwp9LNjsA1jzcdjF6RNGjU8'  # 这里填写Deta的ProjectKey
headers = {
	"User-Agent": ":Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko)Version/5.1 Safari/534.50",
	"content-type": "text/html; charset=utf-8",
}


@app.route("/")
def index():
	return '<h1>你在看叽霸呢？</h1>'


@app.route("/<string:short_code>", methods=['GET'])
def deal_url(short_code):
	return Find_code(short_code)


@app.route("/init")
def init_API():  # 初始化数据库。仅作访问频率限制
	deta = Deta()
	db = deta.Base('API_Stamp')
	ID = db.fetch({'ID': 123}).count
	if not ID:
		db.insert({
			"Stamp": time.time(),
			"ID": 123
		})
	return '<h1>数据库已初始化！</h1>'


def Find_code(FH):
	deta = Deta()
	db = deta.Base('API_Stamp')
	Stamp = db.fetch({'ID': 123}).items[0]
	if time.time() - Stamp['Stamp'] >= 3:
		db.update(key=Stamp['key'], updates={'Stamp': time.time()})
		FH_data = []
		API = "https://javdb.com/search?q=" + FH + "&f=all"
		res = httpx.get(API, headers=headers).text
		soup = bs(res, 'html.parser')
		List = soup.find("div", class_="movie-list")
		Items = List.find_all("div", class_="item")
		i = 0
		Web = soup.find('body').get("data-domain").replace('.', '。')
		for item in Items:
			if i <= 4:
				i += 1
				# Web = 'https://javdb.com'
				url = item.find('a').get("href")
				title = item.find('a').get("title")
				fh = item.find('strong').text
				meta = item.find('div', class_='meta').text.replace(" ", "").replace('\n', '')
				score = item.find('span', class_='value').text.replace(u"\xa0", u"").replace(" ", "").replace('\n', '')
				img = item.find('img').get("src")
				FH_data.append({
					"url": Web + url,
					"title": title,
					"fh": fh,
					"meta": meta,
					"score": score,
					"img": img})
			else:
				break
		return FH_data
	else:
		return 0


if __name__ == '__main__':
	app.run()
