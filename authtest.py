import requests
import hashlib
import time
import json
loginInfo=json.load(open('apikey.json','r'))
private=loginInfo['privatekey']
public=loginInfo['pubkey']
def sendRequest(request):
	stamp=str(time.time())
	hashString=stamp+private+public
	hash=hashlib.md5(hashString.encode()).hexdigest()
	httprequest=requests.get(f'http://gateway.marvel.com/v1/public/{request}?ts={stamp}&apikey={public}&hash={hash}')
	return json.loads(httprequest.text)['data']['results']
print(json.dumps(sendRequest('characters'), sort_keys=True,indent=4, separators=(',', ': ')))