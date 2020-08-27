
import copy
import requests
import json

from mappers import (
    BaseMapper,
    ExpandableMapper
)
from mappers.constants import (
    MANAGER_EXPANDED_RELATIONSHIP,
    OFFICE_EXPANDED_RELATIONSHIP,
    DEPARTMENT_EXPANDED_RELATIONSHIP,
    SUPER_DEPARTMENT_EXPANDED_RELATIONSHIP,
    DEFAULT_EMPTY_RES,
    DEFAULT_ERR_MSG
)
from mappers.office_mapper import OfficeMapper
from mappers.department_mapper import DepartmentMapper

EXTERNAL_API_URL = 'https://rfy56yfcwk.execute-api.us-west-1.amazonaws.com/bigcorp/employees'


class EmployeeMapper(BaseMapper, ExpandableMapper):
    def __init__(self, req=None):
        super().__init__(req)
        self.managers = []

    def get_by_id(self, id):
        if id is None:
            return [{'error': 'Error'}]

        query = 'id={id}'.format(id=id)

        return self.__get_employees(query=query)

    def get_all(self):
        err_msg, query = self.build_query_string()

        if err_msg[0]['error'] != '':
            return err_msg

        return self.__get_employees(query=query)

    def get_relationship_by_id(self, relationship_type, relationship_id):
        if relationship_type == MANAGER_EXPANDED_RELATIONSHIP:
            return self.format_list_to_object(self.__get_manager_by_id(manager_id=relationship_id))
        elif relationship_type == OFFICE_EXPANDED_RELATIONSHIP:
            return self.format_list_to_object(OfficeMapper().get_by_id(id=relationship_id))
        elif relationship_type in [DEPARTMENT_EXPANDED_RELATIONSHIP, SUPER_DEPARTMENT_EXPANDED_RELATIONSHIP]:
            return self.format_list_to_object(DepartmentMapper().get_by_id(id=relationship_id))

        return

    def __perform_request(self, query):
        response = requests.get('{url}?{query}'.format(url=EXTERNAL_API_URL, query=query))

        if response.status_code == 200:
            return DEFAULT_ERR_MSG, json.loads(response.text)
        elif response.status_code == 400:
            return [{'error': response.text}], DEFAULT_EMPTY_RES
        else:
            return [{'error': 'Unable to get Employees'}], DEFAULT_EMPTY_RES

    def __get_all_managers(self, res):
        max_number_of_requests = 0 if self.expanded_relationships is None else len(
            max([list(filter(lambda i: i == MANAGER_EXPANDED_RELATIONSHIP, x.split('.'))) for x in
                 self.expanded_relationships]))

        for _ in range(max_number_of_requests):
            ids_ary = set(x['id'] for x in res)
            manager_ids_ary = set(x[MANAGER_EXPANDED_RELATIONSHIP] for x in
                                  list(filter(lambda x: x[MANAGER_EXPANDED_RELATIONSHIP] is not None, res)))

            excluded_ids_ary = manager_ids_ary - ids_ary

            if len(excluded_ids_ary) > 0:
                query_str = '&'.join(['id={id}'.format(id=itm) for itm in excluded_ids_ary])
                err_msg, this_ary = self.__perform_request(query=query_str)

                if err_msg[0]['error'] != '':
                    return err_msg, DEFAULT_EMPTY_RES

                res += this_ary
            else:
                break

        return DEFAULT_ERR_MSG, res

    def __get_manager_by_id(self, manager_id):
        return list(filter(lambda manager: manager['id'] == int(manager_id), self.managers))

    def __get_employees(self, query):
        err_msg = self.validate_expanded_relationships()

        if err_msg[0]['error'] != '':
            return err_msg

        err_msg, res = self.__perform_request(query=query)

        if err_msg[0]['error'] != '':
            return err_msg

        items = copy.deepcopy(res)
        err_msg, self.managers = self.__get_all_managers(items)

        if err_msg[0]['error'] != '':
            return err_msg

        if self.expanded_relationships is not None:
            return self.expand_relationships(items=res, relationship_getter=self.get_relationship_by_id)
        return res
