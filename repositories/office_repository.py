from mappers.office_mapper import OfficeMapper
from mappers.constants import DEFAULT_ERR_MSG
from repositories import BaseRepository


class BaseOfficeRepository(BaseRepository):
    def __init__(self, req):
        super().__init__(req)
        self.req = req

    def validate_args(self):
        args = super(BaseOfficeRepository, self).validate_args()

        if len(args.keys()) > 0:
            return [{'error': 'Avoid using extra args like: id, limit, offset, expand, etc'}]

        return DEFAULT_ERR_MSG


class OfficeRepository(BaseOfficeRepository):
    def __init__(self, office_id, req):
        super().__init__(req)
        self.office_id = office_id
        self.req = req

    def __call__(self, *args, **kwargs):
        err_msg = self.validate_args()
        if err_msg[0]['error'] == '':
            return OfficeMapper().get_by_id(id=self.office_id)
        return err_msg


class OfficesRepository(BaseOfficeRepository):
    def __init__(self, req):
        super().__init__(req)
        self.req = req

    def __call__(self, *args, **kwargs):
        err_msg = self.validate_args()
        if err_msg[0]['error'] == '':
            return OfficeMapper().get_all()
        return err_msg
