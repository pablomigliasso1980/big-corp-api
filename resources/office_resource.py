from flask import request
from flask_restful import Resource

from repositories.office_repository import (
    OfficeRepository,
    OfficesRepository
)


class OfficeResource(Resource):
    def get(self, office_id):
        return OfficeRepository(office_id=office_id, req=request)()


class OfficesResource(Resource):
    def get(self):
        return OfficesRepository(req=request)()
