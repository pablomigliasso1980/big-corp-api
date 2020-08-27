from flask import request
from flask_restful import Resource

from repositories.department_repository import (
    DepartmentRepository,
    DepartmentsRepository
)


class DepartmentResource(Resource):
    def get(self, department_id):
        return DepartmentRepository(department_id=department_id, req=request)()


class DepartmentsResource(Resource):
    def get(self):
        return DepartmentsRepository(req=request)()
