"""Backend Module

Created on Dec 6, 2012
@author: Chris Boesch
"""
"""
Note to self: json.loads = json string to objects. json.dumps is object to json string.
"""
import datetime
import logging

import webapp2 as webapp

from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app

import json

class Backend(db.Model):
  apikey = db.StringProperty(required=True,default='Default-APIKey')
  model = db.StringProperty(required=True,default='Default-Model')
  #Use backend record id as the model id for simplicity
  jsonString = db.TextProperty(required=True,default='{}')
  created = db.DateTimeProperty(auto_now_add=True) #The time that the model was created    
  modified = db.DateTimeProperty(auto_now=True)
  
  @staticmethod
  def add(apikey, model, data):
    #update ModelCount when adding
    jsonString = data
    entity = Backend(apikey=apikey,
                    model=model,
                    jsonString=jsonString)
    
    entity.put()
    modelCount = ModelCount.all().filter('apikey',apikey).filter('model', model).get()
    if modelCount:
      modelCount.count += 1
      modelCount.put()
    else:
      modelCount = ModelCount(apikey=apikey, model=model, count=1)
      modelCount.put()
    
    result = {'model':model,
              'apikey': apikey,
              'id': entity.key().id(), 
              'data': json.loads(jsonString)} #this would also check if the json submitted was valid
        
    return result
  
  @staticmethod
  def get_entities(apikey, model):
    #update ModelCount when adding
    objects = Backend.all().filter('apikey',apikey).filter('model', model).fetch(50)
    
    entities = []
    for object in objects:
      entity = {'model':model,
              'apikey': apikey,
              'id': object.key().id(), 
              'data': json.loads(object.jsonString)}
      entities.append(entity)
    
    count = 0
    modelCount = ModelCount.all().filter('apikey',apikey).filter('model', model).get()
    if modelCount:
      count = modelCount.count
    result = {'method':'get_entities',
              'apikey': apikey,
              'model': model,
              'count': count,
              'entities': entities}      
    return result
    
  @staticmethod
  def get_entity(apikey,model,model_id):
    theobject = Backend.get_by_id(int(model_id))
    
    result = {'method':'get_model',
                  'apikey': apikey,
                  'model': model,
                  'id': model_id,
                  'data': json.loads(theobject.jsonString)
                  }
    return result
  
  @staticmethod
  def clear(apikey, model):
    #update model count when clearing model on api
    count = 0
    for object in Backend.all().filter('apikey',apikey).filter('model', model):
      count += 1
      object.delete()
      
    modelCount = ModelCount.all().filter('apikey',apikey).filter('model', model).get()
    if modelCount:
      modelCount.delete()
    result = {'items_deleted': count}
    return result
  
  #You can't name it delete since db.Model already has a delete method
  @staticmethod
  def remove(apikey, model, model_id):
  	#update model count when deleting
  	entity = Backend.get_by_id(int(model_id))
  	
  	if entity and entity.apikey == apikey and entity.model == model:
  		entity.delete()
  	
  		result = {'method':'delete_model_success',
                  'apikey': apikey,
                  'model': model,
                  'id': model_id
                  }
  	else:
  		result = {'method':'delete_model_notfound'}
  	
  	return result

  #data is a dictionary that must be merged with current json data and stored. 
  @staticmethod
  def edit_entity(apikey, model, model_id, data):
    jsonString = data
    entity = Backend.get_by_id(int(model_id))
    entity.jsonString = jsonString
    entity.put()
    
    result = {'model':model,
              'apikey': apikey,
              'id': entity.key().id(), 
              'data': json.loads(entity.jsonString)} #this would also check if the json submitted was valid
        
    return result

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
        callback = self.request.get('callback')
        self.response.headers['Content-Type'] = 'application/json'
        if callback:
        	content = str(callback) + '(' + json.dumps(result) + ')'
        	return self.response.out.write(content)
    		
        return self.response.out.write(json.dumps(result)) 

    def metadata(self,apikey):
      	#Fetch all ModelCount records for apikey to produce metadata on currently supported models. 
      	models = []
        for mc in ModelCount.all().filter('apikey',apikey):
          models.append({'model':mc.model, 'count': mc.count})
        result = {'method':'metadata',
                  'apikey': apikey, 
                  'models': models
                  }
      	return self.respond(result)
      
    def clear_apikey(self,apikey):
        """Clears the datastore for a an apikey. 
				"""
        return self.respond({'method':'clear_apikey'})
      
    def clear_model(self,apikey, model):
        """Clears the datastore for a model and apikey.
        """
      	result = Backend.clear(apikey, model)
        return self.respond(result)

    def add_or_list_model(self,apikey,model):
      	#Check for GET paramenter == model to see if this is an add or list. 
      	#Call Backend.add(apikey, model, data) or
        #Fetch all models for apikey and return a list. 
        
      	
        data = self.request.get(model)
        if data: 
          result = Backend.add(apikey, model, data)
        else:
          result = Backend.get_entities(apikey, model)
          
      	return self.respond(result)

    def delete_model(self,apikey,model, model_id):
      	result = Backend.remove(apikey,model, model_id)
      	
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


