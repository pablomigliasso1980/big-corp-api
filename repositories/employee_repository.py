from mappers.employee_mapper import EmployeeMapper
from mappers.constants import (
    VALID_ARGS,
    DEFAULT_ERR_MSG
)
from repositories import BaseRepository


class EmployeeRepository(BaseRepository):
    def __init__(self, employee_id, req):
        super().__init__(req)
        self.employee_id = employee_id
        self.req = req

    def __validate_args(self):
        args = self.validate_args()
        invalid_args = []

        for arg in args.keys():
            if arg in VALID_ARGS:
                invalid_args.append(arg)

        if len(invalid_args) > 0:
            return [{'error': '{} {} {} invalid'.format('These Args: ' if len(invalid_args) > 1 else 'This Arg:',
                                                        ','.join(invalid_args),
                                                        ' are' if len(invalid_args) > 1 else 'is')}]

        return DEFAULT_ERR_MSG

    def __call__(self, *args, **kwargs):
        err_msg = self.__validate_args()
        if err_msg[0]['error'] == '':
            return EmployeeMapper(req=self.req).get_by_id(id=self.employee_id)
        return err_msg


class EmployeesRepository(BaseRepository):
    def __init__(self, req):
        super().__init__(req)
        self.req = req

    def __validate(self):
        return self.validate_args()

    def __call__(self, *args, **kwargs):
        return EmployeeMapper(req=self.req).get_all()
