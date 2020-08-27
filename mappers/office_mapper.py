import os
import json
from mappers import BaseMapper

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

offices_json_file = os.path.join(THIS_FOLDER, 'offices.json')

with open(offices_json_file, "r") as f:
    offices = json.load(f)


class OfficeMapper(BaseMapper):
    def get_by_id(self, id):
        if id is None:
            return [{'error': 'Error'}]

        return list(filter(lambda office: office['id'] == int(id), offices))

    def get_all(self):
        return offices
