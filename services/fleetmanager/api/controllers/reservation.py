from api.models.reservation import ReservationDB
from api.models.exception import *

class ReservationController:
    """Controller for Reservation
    """
    def create_reservation(self, payload):
        if payload["fromdate"] > payload["todate"]:
            return {"message": "issue with from/to date"}, 409

        if self._overlap(payload):
            return {"message":"Found conflicting reservation"}, 409
        else:
            id = ReservationDB().create(payload)
            return id, 201

    def get_reservation(self, prod_id):
        try:
            payload = ReservationDB().get(prod_id)
            return payload, 200
        except ResourceNotFoundException as exc:
            return dict(message=str(exc)), 404

    def list_reservation(self, filterPayload):
        try:
            return ReservationDB().list(**filterPayload), 200
        except Exception as exc:
            return dict(message=str(exc)), 500

    def delete_reservation(self, id):
        try:
            id = ReservationDB().delete(id)
            return id, 200
        except ResourceNotFoundException as exc:
            return dict(message=str(exc)), 404

    def _overlap(self, payload):
        """Check whether 2 reservations overlap
        """
        reservations = ReservationDB().list(selector={"itemname": payload["itemname"]})
        for reservation in reservations:
            if (reservation["fromdate"] >= payload["fromdate"]) and (reservation["fromdate"] < payload["todate"]) or \
                reservation["todate"] > payload["fromdate"] and reservation["todate"] <= payload["todate"]:
                return True
            if (payload["fromdate"] >= reservation["fromdate"]) and (payload["fromdate"] < reservation["todate"]) or \
                (payload["todate"] > reservation["fromdate"]) and (payload["todate"] <= reservation["todate"]):
                return True
        return False
