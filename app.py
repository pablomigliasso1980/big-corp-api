from flask import Flask
from flask_restful import Api

from resources.employee_resource import (
    EmployeeResource,
    EmployeesResource,
)
from resources.department_resource import (
    DepartmentResource,
    DepartmentsResource
)
from resources.office_resource import (
    OfficeResource,
    OfficesResource
)

app = Flask(__name__)
api = Api(app)

api.add_resource(EmployeeResource, '/employees/<int:employee_id>')
api.add_resource(EmployeesResource, '/employees/')

api.add_resource(DepartmentResource, '/departments/<int:department_id>')
api.add_resource(DepartmentsResource, '/departments/')

api.add_resource(OfficeResource, '/offices/<int:office_id>')
api.add_resource(OfficesResource, '/offices/')

if __name__ == '__main__':
    app.run(debug=True)
