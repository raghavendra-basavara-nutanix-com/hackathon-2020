from datetime import datetime
from datetime import date
from api.models.tenant import NuTestDBClient
# from api.controllers.reservation import ReservationController
from api.models.exception import *
from lib.fleet_update import get_fleets_from_canaveral

class TenantController:
    """Controller for Tenant
    """
    def list_tenants(self, filterPayload):
       try:
           return NuTestDBClient().list(**filterPayload), 200
       except Exception as exc:
           return dict(message=str(exc)), 500

    def get_tenant_reservations(self, table_name):
        try:
            data = NuTestDBClient().get(prod_id)
            # data = self.db[id]
            # reservations = ReservationDB().list(selector={"itemname": id})
            reservations = NuTestDBClient().list(selector={"itemname": prod_id})
            res = []
            for reservation in reservations:
                res.append({"tenantName": data["_id"], "stage": data["insights_data"]["fleet"]["metadata"]["stage"],
                            "owner": reservation["owner"], "description": reservation["description"],
                            "fromdate": reservation["fromdate"], "todate": reservation["todate"],
                            "reservation_id": reservation["_id"]})
            # sort by from date
            return res[:10], 200
        except ResourceNotFoundException as exc:
            return dict(message=str(exc)), 404
        #return NuTestDBClient().list_reservation(prod_id)

    def get_tenant_line(self, prod_id):
        try:
            payload = NuTestDBClient().list(prod_id)
            final_payload = []
            for dictn in payload:
              cont_lines = []
              for line in dictn['lines']:
                if line.strip() == ",":
                  continue
                line = line.replace("\n", "<br>")
                cont_lines.append(line)
              dictn['lines'] = cont_lines

              final_payload.append(dictn)
            lines = {
                "data": final_payload
            }
            print (lines)
            return lines, 200
        except ResourceNotFoundException as exc:
            return dict(message=str(exc)), 404

    def get_tenant_line_id(self, table, prod_id):
      try:
        payload = NuTestDBClient().get(table, prod_id)
        return payload, 200
      except ResourceNotFoundException as exc:
        return dict(message=str(exc)), 404

def resolver():
    """return operation handlers for connexion to use for deployment resource
    Arguments:
        config {dict} -- configurations for the web app
    Returns:
        dict -- operation handlers
    """
    tenant_controller = TenantController()
    op_map = {
        "get_tenant_line": tenant_controller.get_tenant_line,
        "get_tenant_line_id": tenant_controller.get_tenant_line_id,
        "get_tenant_reservations": tenant_controller.get_tenant_reservations,
        "list_tenants": tenant_controller.list_tenants
    }
    return op_map