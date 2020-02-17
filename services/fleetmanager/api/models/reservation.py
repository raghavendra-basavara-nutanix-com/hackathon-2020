import requests
import couchdb
import os
from lib.fleet_update import get_fleets_from_canaveral
from datetime import datetime
from datetime import date

# ADMIN_USERNAME = 'admin'
# ADMIN_PASSWORD = 'pass'
# COUCHDB_URL = 'http://'+ADMIN_USERNAME+':'+ADMIN_PASSWORD+'@127.0.0.1:5984/'
ADMIN_USERNAME = os.environ.get('DATABASE_USER')
ADMIN_PASSWORD = os.environ.get('DATABASE_PASSWORD')
DB_PORT = os.environ.get('DATABASE_PORT')
COUCHDB_URL = 'http://'+ADMIN_USERNAME+':'+ADMIN_PASSWORD+'@127.0.0.1:'+DB_PORT+'/'

couch = couchdb.Server(COUCHDB_URL)

class ReservationDB(object):

    RESOURCE = "Reservation"
    DBNAME = "reservation2"

    def __init__(self):
        """Initialize reservation database
        """
        if self.DBNAME in couch:
            self.db = couch[self.DBNAME]
        else:
            self.db = couch.create(self.DBNAME)

    def create(self,payload):
        """Create a reservation entry
        """
        id = self.db.save(payload)
        return id

    def get(self, id):
        """Return a particular reservation data
        """
        if (id in self.db):
            return self.db[id]
        else:
            raise ResourceNotFoundException(self.RESOURCE, id)

    def delete(self, id):
        """Delete a particular reservation
        """
        if (id in self.db):
            self.db.delete(self.db[id])
            return id
        else:
            raise ResourceNotFoundException(self.RESOURCE, id)

    def list(self, selector=None, fields=None):
        """List all reservations
        """
        if not selector:
            selector = {}

        query = {'selector': selector}
        if fields:
            query["fields"] = fields

        tenants = []
        tenant_list = self.db.find(query)
        for tenant in tenant_list:
            tenants.append(tenant)

        return tenants
