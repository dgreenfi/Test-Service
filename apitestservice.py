import webapp2
import json
from google.appengine.api import urlfetch
import sys
import urllib
import random
import re
import logging



class MainPage(webapp2.RequestHandler):
    def get(self):
        obj = {
        'success': 'Yes',
        'Boo': 'Yah',
         }
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps(obj))

class Sentiment(webapp2.RequestHandler):
    def get(self):

        api_key = self.request.get('api_key')
        posts=int(self.request.get('posts'))
        license_id=self.request.get('license_id')
        dummy=self.request.get('dummy')
        alc_key=self.request.get('alc_key')
        ALC_URL='http://access.alchemyapi.com/calls/text/TextGetTextSentiment?outputMode=json&apikey='+alc_key+'&text='
        perc_url='https://percolate.com/api/v4/post_set/?order_by=release_at&order_direction=desc&license_id='+license_id+'&api_key='+api_key+'&limit='+str(posts)
        # The whole MultiDict:
         # GET([('check', 'a'), ('check', 'b'), ('name', 'Bob')])
        #url = "http://www.google.com/"
        percreq=urlfetch.fetch(perc_url)
        logging.debug(percreq.content)
        percposts= json.loads(percreq.content)

        ents=[]

        for post in percposts['data'][0:posts]:
            if dummy=='yes':
                rjson={'status':'OK','docSentiment':{'score':str((random.random()*2)-1),'type':'fake'}}
            if dummy<>'yes':
                result = urlfetch.fetch(ALC_URL+urllib.quote_plus(re.sub(r'[^\w]', ' ',  post['body'])))
                logging.debug(result.content)
                rjson=json.loads(result.content)
            if rjson['status']=='OK':
                ents.append({"post":post['body'],"sentiment":rjson['docSentiment'],'published_at':post['posts'][0]['published_at']})
            else:
                ents.append({"post":post['body'],"sentiment":{"score":0},'published_at':post['posts'][0]['published_at']})
        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps({"data":ents}))

class Entities(webapp2.RequestHandler):
    def get(self):

        api_key = self.request.get('api_key')
        posts=int(self.request.get('posts'))
        license_id=self.request.get('license_id')
        ALC_URL='http://access.alchemyapi.com/calls/text/TextGetRankedNamedEntities?outputMode=json&apikey='+ALC_KEY+'&text='
        perc_url='https://percolate.com/api/v4/post_set/?order_by=release_at&order_direction=desc&license_id='+license_id+'&api_key='+api_key
        # The whole MultiDict:
         # GET([('check', 'a'), ('check', 'b'), ('name', 'Bob')])
        #url = "http://www.google.com/"
        percreq=urlfetch.fetch(perc_url)
        percposts= json.loads(percreq.content)
        print percposts
        posttexts=[post['body'] for post in percposts['data']]
        ents=[]

        for post in posttexts[0:posts]:
            result = urlfetch.fetch(ALC_URL+urllib.quote_plus(post))
            rjson=json.loads(result.content)
            ents.append({"post":post,"entities":rjson['entities']})

        self.response.headers['Content-Type'] = 'application/json'
        self.response.out.write(json.dumps({"data":ents}))


application = webapp2.WSGIApplication([
    ('/', MainPage),
    (r'/sentiment', Sentiment),
    (r'/entities', Entities),
], debug=True)



