import copy
import json
import os
from mappers import (
    BaseMapper,
    ExpandableMapper
)
from mappers.constants import (
    DEPARTMENT_EXPANDED_RELATIONSHIP,
    SUPER_DEPARTMENT_EXPANDED_RELATIONSHIP
)

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

departments_json_file = os.path.join(THIS_FOLDER, 'departments.json')

with open(departments_json_file, "r") as f:
    departments = json.load(f)


class DepartmentMapper(BaseMapper, ExpandableMapper):
    def __init__(self, req=None):
        super().__init__(req)

    def get_by_id(self, id):
        if id is None:
            return [{'error': 'Error'}]

        err_msg = self.validate_expanded_relationships()

        if err_msg[0]['error'] != '':
            return err_msg

        items = self.__by_id(id)

        return self.__get_departments(items)

    def get_all(self):
        err_msg = self.validate_expanded_relationships()

        if err_msg[0]['error'] != '':
            return err_msg

        items = copy.deepcopy(departments)

        return self.__get_departments(items)

    def get_relationship_by_id(self, relationship_type, relationship_id):
        if relationship_type in [DEPARTMENT_EXPANDED_RELATIONSHIP, SUPER_DEPARTMENT_EXPANDED_RELATIONSHIP]:
            return self.format_list_to_object(self.__by_id(id=relationship_id))
        return

    def __get_departments(self, items):
        if self.expanded_relationships is not None:
            return self.expand_relationships(items=items, relationship_getter=self.get_relationship_by_id)
        return items

    def __by_id(self, id):
        return list(filter(lambda department: department['id'] == int(id), departments))
