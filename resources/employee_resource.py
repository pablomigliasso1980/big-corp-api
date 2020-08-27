from flask import request
from flask_restful import Resource
from repositories.employee_repository import (
    EmployeeRepository,
    EmployeesRepository
)


class EmployeeResource(Resource):
    def get(self, employee_id):
        return EmployeeRepository(employee_id=employee_id, req=request)()


class EmployeesResource(Resource):
    def get(self):
        return EmployeesRepository(req=request)()


