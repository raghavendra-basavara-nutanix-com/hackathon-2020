import pymongo
from bson.objectid import ObjectId

# database_name = nutest_test_db
# table names: class_prerun_logs, class_setup_logs, test_prerun_logs, test_setup_logs, test_body_logs
# test_teardown_logs, test_portun_logs, class_teardown_logs, class_postrun_logs

class NuTestDBClient:

  def __init__(self, db_name="nutest_test_db"):
    nutest_db_client = pymongo.MongoClient("mongodb://localhost:27017/")
    db_obj = nutest_db_client[db_name]
    self.db_obj = db_obj

  def insert(self, table, entry):
    self.db_obj[table].insert_one(entry)

  def insert_many(self, table, entries):
    self.db_obj[table].insert_many(entries)

  def get(self, table, id):
    id = ObjectId(id)
    obj = self.db_obj[table].find({'_id': id})
    lines = []
    for line in obj:
      line['_id'] = str(line['_id'])
      lines.append(line)
    return lines

  def list(self, table):
    #obj = self.db_obj[table].find({}, {"_id": 0})
    obj = self.db_obj[table].find()
    lines = []
    for line in obj:
      line['_id'] = str(line['_id'])
      lines.append(line)
    return lines