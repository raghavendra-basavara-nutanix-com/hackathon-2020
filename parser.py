import os
import json
import re

from DBInterface import NuTestDBClient

module_regex = re.compile(".* (\w+.py):.*")
dash_line = re.compile("-{5,}")
db_client = NuTestDBClient(db_name="nutest_test_db")

product_calls = { "ssh_calls": set(), "rest_calls": set()}

for (root, _, files) in os.walk("../logs/20180402_230039/"):
  if "nutest_test.log" in files:
    test_log_path = os.path.join(root, "nutest_test.log")
  if "nutest_class.log" in files:
    class_log_path = os.path.join(root, "nutest_class.log")
  if "nutest.log" in files:
    nutest_log_path = os.path.join(root, "nutest.log")

with open(nutest_log_path, "r") as fh:
  for line in fh.readlines():
    if "Nutest Branch" in line:
      m = re.match(".*Nutest Branch: (\w+)\n*", line)
      nutest_branch = m.groups()[0]
    if "Nutest Commit" in line:
      m = re.search(".*Nutest Commit: (\w+)\n*", line)
      nutest_commit = m.groups()[0]

logwise_json = {
  "nutest_branch": nutest_branch,
  "nutest_commit": nutest_commit,
  "stage_execn_stats": {}
}

with open("logwise.json", "w") as fh:
  json.dump(logwise_json, fh)

def _look_for_prod_apis(line):
  if ">>" in line:
    if "ssh.py" in line:
      command = line.split(">>")[1]
      product_calls['ssh_calls'].add(command)
    if "http.py" in line:
      command = line.split(">>")[1]
      product_calls['rest_calls'].add(command)

def _update_stage_time_and_status(stage, line):
  m = re.search("completed in (\d+s)", line)
  time = m.groups()[0]

  with open("logwise.json", "r") as fh:
    json_content = json.load(fh)
    json_content['stage_execn_stats'][stage] = {"status": "completed", "time_taken": time}

  with open("logwise.json", "w") as fh:
    json.dump(json_content, fh)
##
## handling class logs
##

log_handler = open(class_log_path, "r")

class_preruns = []
class_setups = []
class_teardowns = []
class_postruns = []

class_prerun = False
class_setup = False
class_teardown = False
class_postrun = False

for line in log_handler.readlines():
  _look_for_prod_apis(line)
  if dash_line.search(line):
    continue

  if "CLASS PRERUN" in line and not "completed" in line:
    class_prerun = True
    continue
  if "CLASS PRERUN completed in" in line:
    _update_stage_time_and_status("CLASS PRERUN", line)
    class_prerun = False
  if class_prerun:
    class_preruns.append(line)

  if "CLASS SETUP" in line and not "completed" in line:
    class_setup = True
    continue
  if "CLASS SETUP completed in" in line:
    _update_stage_time_and_status("CLASS SETUP", line)
    class_setup = False
  if class_setup:
    class_setups.append(line)

  if "CLASS TEARDOWN" in line and not "completed" in line:
    class_teardown = True
    continue
  if "CLASS TEARDOWN completed in" in line:
    _update_stage_time_and_status("CLASS TEARDOWN", line)
    class_teardown = False
  if class_teardown:
    class_teardowns.append(line)

  if "CLASS POST RUN" in line and not "completed" in line:
    class_postrun = True
    continue
  if "CLASS POSTRUN completed in" in line:
    _update_stage_time_and_status("CLASS POSTRUN", line)
    class_postrun = False
  if class_postrun:
    class_postruns.append(line)

fc = []
if class_preruns:
  for line in class_preruns: 
    match = module_regex.search(line)
    if match:
      module = match.groups()[0]
      fc.append({'module': module, 'lines': [line]})
    else:
      fc[-1]['lines'].append(line)

  db_client.insert_many('class_preruns', fc)
  fc = []

if class_setups:
  for line in class_setups:
    match = module_regex.search(line)
    if match:
      module = match.groups()[0]
      fc.append({'module': module, 'lines': [line]})
    else:
      fc[-1]['lines'].append(line)

  db_client.insert_many('class_setup', fc)
  fc = []

if class_teardowns:
  for line in class_teardowns:
    match = module_regex.search(line)
    if match:
      module = match.groups()[0]
      fc.append({'module': module, 'lines': [line]})
    else:
      fc[-1]['lines'].append(line)

  with open("class_teardowns.json", "w") as class_teardown_fh:
    json.dump(fc, class_teardown_fh)

  db_client.insert_many('class_teardown', fc)
  fc = []

if class_postruns:
  for line in class_postruns:
    match = module_regex.search(line)
    if match:
      module = match.groups()[0]
      fc.append({'module': module, 'lines': [line]})
    else:
      fc[-1]['lines'].append(line)

  db_client.insert_many('class_postrun', fc)
  fc = [] 

##
## handling test logs
##

log_handler = open(test_log_path, "r")

test_preruns = []
test_setups = []
test_teardowns = []
test_postruns = []
test_bodyc = []

test_prerun = False
test_setup = False
test_teardown = False
test_postrun = False
test_body = False

lines = log_handler.readlines()

m = re.search("name:testcases.(.*)\n*", lines[0])
test_name = m.groups()[0]

for line in lines:
  if dash_line.search(line):
    continue

  if "TEST PRERUN" in line and not "completed" in line:
    test_prerun = True
    continue
  if "TEST PRERUN completed in" in line:
    _update_stage_time_and_status("TEST PRERUN", line)
    test_prerun = False
  if test_prerun:
    test_preruns.append(line)

  if "TEST SETUP" in line and not "completed" in line:
    test_setup = True
    continue
  if "TEST SETUP completed in" in line:
    _update_stage_time_and_status("TEST SETUP", line)
    test_setup = False
  if test_setup:
    test_setups.append(line)

  if "TEST BODY" in line and not "completed" in line:
    test_body = True
    continue
  if "TEST BODY completed in" in line:
    _update_stage_time_and_status("TEST BODY", line)
    test_body = False
  if test_body:
    test_bodyc.append(line)

  if "TEST TEARDOWN" in line and not "completed" in line:
    test_teardown = True
    continue
  if "TEST TEARDOWN completed in" in line:
    _update_stage_time_and_status("TEST TEARDOWN", line)
    test_teardown = False
  if test_teardown:
    test_teardowns.append(line)

  if "TEST POSTRUN" in line and not "completed" in line:
    test_postrun = True
    continue
  if "Test Post Run completed in" in line:
    _update_stage_time_and_status("TEST POSTRUN", line)
    test_postrun = False
  if test_postrun:
    test_postruns.append(line)

fc = []

if test_preruns:
  for line in test_preruns:
    match = module_regex.search(line)
    if match:
      module = match.groups()[0]
      fc.append({'module': module, 'lines': [line]})
    else:
      fc[-1]['lines'].append(line)

  db_client.insert_many('test_prerun', fc)
  fc = []

if test_setups:
  for line in test_setups:
    match = module_regex.search(line)
    if match:
      module = match.groups()[0]
      fc.append({'module': module, 'lines': [line]})
    else:
      fc[-1]['lines'].append(line)

  db_client.insert_many('test_setup', fc)
  fc = []

if test_bodyc:
  for line in test_bodyc:
    match = module_regex.search(line)
    if match:
      module = match.groups()[0]
      fc.append({'module': module, 'lines': [line]})
    else:
      fc[-1]['lines'].append(line)

  db_client.insert_many('test_body', fc)
  fc = []

if test_teardowns:
  for line in test_teardowns:
    match = module_regex.search(line)
    if match:
      module = match.groups()[0]
      fc.append({'module': module, 'lines': [line]})
    else:
      fc[-1]['lines'].append(line)

  db_client.insert_many('test_teardown', fc)
  fc = []

if test_postruns:
  for line in test_postruns:
    match = module_regex.search(line)
    if match:
      module = match.groups()[0]
      fc.append({'module': module, 'lines': [line]})
    else:
      fc[-1]['lines'].append(line)

  db_client.insert_many('test_postrun', fc)
  fc = []

product_calls['ssh_calls'] = list(product_calls['ssh_calls'])
product_calls['rest_calls'] = list(product_calls['rest_calls'])

with open("logwise.json", "r") as logwise_fh:
  logwise_content = json.load(logwise_fh)

with open("logwise.json", "w") as logwise_fh:
  logwise_content['product_calls'] = product_calls
  logwise_content['test_name'] = test_name
  json.dump(logwise_content, logwise_fh)
