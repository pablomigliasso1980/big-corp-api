from common.utils import ApiBuilder
from common.utils import (
    DEPARTMENTS_REQUEST,
    VALID_ARGS,
    SUPER_DEPARTMENT_EXPANDED_RELATIONSHIP,
    EXPAND_ARG,
    DEFAULT_ERR_MSG
)
from repositories import BaseRepository


class BaseDepartmentRepository(BaseRepository):
    def __init__(self, req):
        super().__init__(req)
        self.req = req

    def validate_args(self):
        args = super(BaseDepartmentRepository, self).validate_args()
        invalid_args = []

        for arg_key, arg_val in args.items():
            if arg_key in VALID_ARGS:
                invalid_args.append(arg_key)
            elif arg_key == EXPAND_ARG:
                expanded_args = []

                for expanded_arg in [item.split('.') for item in arg_val]:
                    expanded_args += expanded_arg

                expanded_args = set(expanded_args)

                for this_arg in expanded_args:
                    if this_arg != SUPER_DEPARTMENT_EXPANDED_RELATIONSHIP:
                        invalid_args.append(this_arg)

        if len(invalid_args) > 0:
            return [{'error': '{} {} {} invalid'.format('These Args: ' if len(invalid_args) > 1 else 'This Arg:',
                                                        ','.join(invalid_args),
                                                        ' are' if len(invalid_args) > 1 else 'is')}]

        return DEFAULT_ERR_MSG


class DepartmentRepository(BaseDepartmentRepository):
    def __init__(self, department_id, req):
        super().__init__(req)
        self.department_id = department_id
        self.req = req

    def __call__(self, *args, **kwargs):
        err_msg = self.validate_args()
        if err_msg[0]['error'] == '':
            return ApiBuilder(req=self.req)(perform_request_type=DEPARTMENTS_REQUEST, department_id=self.department_id)
        return err_msg


class DepartmentsRepository(BaseDepartmentRepository):
    def __init__(self, req):
        super().__init__(req)
        self.req = req

    def __call__(self, *args, **kwargs):
        err_msg = self.validate_args()
        if err_msg[0]['error'] == '':
            return ApiBuilder(req=self.req)(perform_request_type=DEPARTMENTS_REQUEST)
        return err_msg
