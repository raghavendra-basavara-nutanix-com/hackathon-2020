from lib.http import HTTP
import json
import pprint
import os

def get_canaveral_token(**kwargs):
    """

    :return:
    """
    payload = {
        "credential": {
            "type": "ldap",
            "mechanism": "user+pass",
            "payload": {
         	    "username": os.environ.get('CANAVERAL_USER'),
                "password": os.environ.get('CANAVERAL_PASSWORD'),
                "realm": "corp.nutanix.com"
            }
        }
    }
    http = HTTP()
    http.headers = {'Content-Type': 'application/json'}
    url = "https://canaveral-gatekeeper.canaveral-corp.us-west-2.aws/auth"
    retries = kwargs.pop("retries", 2)
    retry_interval = kwargs.pop("retry_interval", 3)
    params = kwargs.pop("params", {})
    try:
        response = http.post(url, params=params, retries=retries,
                             retry_interval=retry_interval, json=payload, **kwargs)
        response = json.loads(response.content)
        # if response['success']:
        #   return response
        # raise Exception("Resource is not available in %s" % JARVIS_URL)
    except Exception as exc:
        raise

    return response["result"]

def get_fleets_from_canaveral(**kwargs):
    """

    :return:
    """
    token = get_canaveral_token()

    http = HTTP()
    headers = {'Authorization': token}
    http._session.headers.update(headers)
    url = "https://canaveral-fleet-manager.canaveral-corp.us-west-2.aws/fleets"
    retries = kwargs.pop("retries", 2)
    retry_interval = kwargs.pop("retry_interval", 3)
    params = kwargs.pop("params", {})
    try:
        response = http.get(url, params=params, retries=retries,
                             retry_interval=retry_interval)
        response = json.loads(response.content)
        # if response['success']:
        #   return response
        # raise Exception("Resource is not available in %s" % JARVIS_URL)
    except Exception as exc:
        raise Exception("Failed to get canaveral token")

    data = response

    selected_tenants = []
    for tenant in data["result"]:
        if tenant.get("service", {}).get("org") \
                and tenant.get("service", {}).get("name") \
                and tenant["service"]["org"] == "xi-integrationtesting" \
                and tenant["service"]["name"] == "fleets":
            selected_tenants.append(tenant)

    tenants_for_xiintest = []
    tenant_types_xiintest = ["DEVTEST", "CANARY", "TEST"]
    test_tenants = []

    for tenant in selected_tenants:
        if tenant.get("fleet", {}).get("metadata", {}).get("tenant_type") \
                and tenant["fleet"]["metadata"]["tenant_type"] in tenant_types_xiintest:
            test_tenants.append(tenant)

    return test_tenants
