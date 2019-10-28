import requests
import hashlib
import time
import json
public='05e07ce2914b79046f157b3f7eee36b3'
private='c1e103dcdbd9d9c0bec980663077e52b346317e2'
def sendRequest(request):
	stamp=str(time.time())
	part=stamp+private+public
	hash=hashlib.md5(part.encode()).hexdigest()
	httprequest=requests.get(f'http://gateway.marvel.com/v1/public/{request}?ts={stamp}&apikey={public}&hash={hash}')
	return json.loads(httprequest.text)['data']
print(sendRequest('comics'))