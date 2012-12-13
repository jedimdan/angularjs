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
      	result = {'method':'metadata',
                  'apikey': apikey
                  }
      	return self.respond(result)

    def add_or_list_model(self,apikey,model):
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
      
    def clear_apikey(self,apikey):
        """Clears the datastore for a model and key.
        """
        return self.respond({'method':'clear_apikey'})
      
    def clear_model(self,apikey, model):
        """Clears the datastore for a model and key.
        """
        return self.respond({'method':'clear_model'})
               
          
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
