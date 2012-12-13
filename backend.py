"""Backend Module

Created on Dec 6, 2012
@author: Chris Boesch
"""

import datetime
import logging

import webapp2 as webapp

from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app

from django.utils import simplejson as json


class Backend(db.Model):
  apikey = db.StringProperty(required=True,default='Default-APIKey')
  model = db.StringProperty(required=True,default='Default-Model')
  #Use backend record id as the model id for simplicity
  jsonString = db.TextProperty(required=True,default='{}')
  created = db.DateTimeProperty(auto_now_add=True) #The time that the model was created    
  modified = db.DateTimeProperty(auto_now=True)
  
  def add(self, apikey, model, data):
    #update ModelCount when adding
    pass
  
  def clear(self,apikey, model):
    #update model count when clearing model on api
    pass
  
  def delete(self,apikey, model, model_id):
    #update model count when deleting
    pass

  #data is a dictionary that must be merged with current json data and stored. 
  def edit(self,apikey, model, model_id, data):
    pass

#Quick retrieval for supported models metadata and count stats
class ModelCount(db.Model):
  apikey = db.StringProperty(required=True,default='Default-APIKey')
  model = db.StringProperty(required=True,default='Default-Model')
  count = db.IntegerProperty(required=True, default=0)
  created = db.DateTimeProperty(auto_now_add=True) #The time that the model was created    
  modified = db.DateTimeProperty(auto_now=True)
  

class ActionHandler(webapp.RequestHandler):
    """Class which handles bootstrap procedure and seeds the necessary
    entities in the datastore.
    """
        
    def respond(self,result):
        """Returns a JSON response to the client.
        """
        self.response.headers['Content-Type'] = 'application/json'
        return self.response.out.write(json.dumps(result)) 

    def metadata(self,apikey):
      	#Fetch all ModelCount records for apikey to produce metadata on currently supported models. 
      	result = {'method':'metadata',
                  'apikey': apikey
                  }
      	return self.respond(result)
      
    def clear_apikey(self,apikey):
        """Clears the datastore for a an apikey. 
				"""
        return self.respond({'method':'clear_apikey'})
      
    def clear_model(self,apikey, model):
        """Clears the datastore for a model and apikey.
        """
        return self.respond({'method':'clear_model'})

    def add_or_list_model(self,apikey,model):
      	#Check for GET paramenter == model to see if this is an add or list. 
      	#Call Backend.add(apikey, model, data) or
        #Fetch all models for apikey and return a list. 
      	result = {'method':'add_or_list_model',
                  'apikey': apikey,
                  'model': model}
      	return self.respond(result)

    def delete_model(self,apikey,model, model_id):
      	result = {'method':'delete_model',
                  'apikey': apikey,
                  'model': model,
                  'id': model_id
                  }
      	return self.respond(result)
      
    def get_or_edit_model(self,apikey,model, model_id):
      	result = {'method':'get_or_edit_model',
                  'apikey': apikey,
                  'model': model,
                  'id': model_id
                  }
      	return self.respond(result)
                    
application = webapp.WSGIApplication([
    webapp.Route('/<apikey>/metadata', handler=ActionHandler, handler_method='metadata'), 
    webapp.Route('/<apikey>/clear', handler=ActionHandler, handler_method='clear_apikey'),
    webapp.Route('/<apikey>/<model>/clear', handler=ActionHandler, handler_method='clear_model'), 
    webapp.Route('/<apikey>/<model>', handler=ActionHandler, handler_method='add_or_list_model'),
    webapp.Route('/<apikey>/<model>/<model_id>/delete', handler=ActionHandler, handler_method='delete_model'), 
    webapp.Route('/<apikey>/<model>/<model_id>', handler=ActionHandler, handler_method='get_or_edit_model'), 
    ],
    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
