import json
import os
import requests
import copy
from urllib.parse import urlparse, parse_qs, unquote

EXTERNAL_API_URL = 'https://rfy56yfcwk.execute-api.us-west-1.amazonaws.com/bigcorp/employees'
EXPAND_ARG = 'expand'
VALID_ARGS = ['id', 'limit', 'offset']

MANAGER_EXPANDED_RELATIONSHIP = 'manager'
OFFICE_EXPANDED_RELATIONSHIP = 'office'
DEPARTMENT_EXPANDED_RELATIONSHIP = 'department'
SUPER_DEPARTMENT_EXPANDED_RELATIONSHIP = 'superdepartment'
VALID_EXPANDED_RELATIONSHIPS = [
    MANAGER_EXPANDED_RELATIONSHIP,
    OFFICE_EXPANDED_RELATIONSHIP,
    DEPARTMENT_EXPANDED_RELATIONSHIP,
    SUPER_DEPARTMENT_EXPANDED_RELATIONSHIP
]

EMPLOYEES_REQUEST = 'employees_request'
DEPARTMENTS_REQUEST = 'departments_request'
OFFICES_REQUEST = 'offices_request'

DEFAULT_ERR_MSG = [{'error': ''}]
DEFAULT_EMPTY_RES = []

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

departments_json_file = os.path.join(THIS_FOLDER, 'departments.json')
offices_json_file = os.path.join(THIS_FOLDER, 'offices.json')

with open(departments_json_file, "r") as f:
    departments = json.load(f)

with open(offices_json_file, "r") as f:
    offices = json.load(f)


class ApiBuilder:
    def __init__(self, req):
        common_args = parse_qs(urlparse(unquote(req.url)).query)
        expanded_relationships = common_args.pop(EXPAND_ARG, None)

        self.common_args = common_args
        self.expanded_relationships = expanded_relationships

        self.managers = []

    def __get_manager_by_id(self, manager_id):
        result = list(filter(lambda manager: manager['id'] == int(manager_id), self.managers))

        if len(result) > 0:
            return result[0]
        return None

    def __get_department_by_id(self, department_id):
        result = list(filter(lambda department: department['id'] == int(department_id), departments))

        if len(result) > 0:
            return result[0]
        return None

    def __get_office_by_id(self, office_id):
        result = list(filter(lambda office: office['id'] == int(office_id), offices))

        if len(result) > 0:
            return result[0]
        return None

    def __get_relationship_by_id(self, relationship_type, relationship_id):
        if relationship_type == MANAGER_EXPANDED_RELATIONSHIP:
            return self.__get_manager_by_id(manager_id=relationship_id)
        elif relationship_type == OFFICE_EXPANDED_RELATIONSHIP:
            return self.__get_office_by_id(office_id=relationship_id)
        elif relationship_type in [DEPARTMENT_EXPANDED_RELATIONSHIP, SUPER_DEPARTMENT_EXPANDED_RELATIONSHIP]:
            return self.__get_department_by_id(department_id=relationship_id)

        return

    def __populate_relationship(self, this_item, hierarchy):
        if this_item.get(hierarchy['relationship'], None) is not None:
            if isinstance(this_item[hierarchy['relationship']], int):
                relationship = self.__get_relationship_by_id(relationship_type=hierarchy['relationship'],
                                                             relationship_id=this_item[hierarchy['relationship']])

                if relationship is not None:
                    this_item[hierarchy['relationship']] = copy.copy(relationship)

                    if hierarchy['children'] is not None:
                        self.__populate_relationship(this_item=this_item[hierarchy['relationship']],
                                                     hierarchy=hierarchy['children'])
            elif isinstance(this_item[hierarchy['relationship']], object):
                if hierarchy['children'] is not None:
                    self.__populate_relationship(this_item=this_item[hierarchy['relationship']],
                                                 hierarchy=hierarchy['children'])

    def __build_relationship_hierarchies(self):
        result = []

        for relationships in self.expanded_relationships:
            children = None

            for rel in relationships.split('.')[::-1]:
                hierarchy = {
                    'relationship': rel,
                    'children': children
                }
                children = hierarchy

            result.append(hierarchy)

        return result

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
                err_msg, this_ary = self.__peform_employees_request(query=query_str)

                if err_msg[0]['error'] != '':
                    return err_msg, DEFAULT_EMPTY_RES

                res += this_ary
            else:
                break

        return DEFAULT_ERR_MSG, res

    def __expand_relationships(self, items):
        relationship_hierarchies = self.__build_relationship_hierarchies()

        for item in items:
            for hierarchy in relationship_hierarchies:
                self.__populate_relationship(this_item=item, hierarchy=hierarchy)

        return items

    def __validate_args(self, args, valid_args):
        invalid_args = []

        for arg in args:
            if arg not in valid_args:
                invalid_args.append(arg)

        if len(invalid_args) > 0:
            return [{'error': '{} {} {} invalid'.format('These Args: ' if len(invalid_args) > 1 else 'This Arg:',
                                                        ','.join(invalid_args),
                                                        ' are' if len(invalid_args) > 1 else 'is')}]
        return DEFAULT_ERR_MSG

    def __validate_expanded_relationships(self):
        if self.expanded_relationships is not None:
            args = []
            for arg in [item.split('.') for item in self.expanded_relationships]:
                args += arg

            return self.__validate_args(args=set(args), valid_args=VALID_EXPANDED_RELATIONSHIPS)
        return DEFAULT_ERR_MSG

    def __build_query_string(self):
        err_msg = self.__validate_args(args=self.common_args.keys(), valid_args=VALID_ARGS)

        if err_msg[0]['error'] == '':
            ary = []
            for key, values in self.common_args.items():
                ary += ['{arg}={value}'.format(arg=key, value=value) for value in values]
            return DEFAULT_ERR_MSG, '&'.join(ary)

        return err_msg, DEFAULT_EMPTY_RES

    def __peform_employees_request(self, query, employee_id=None):
        if employee_id is not None:
            query += '{operand}id={id}'.format(operand='' if query == '' else '&', id=employee_id)
        response = requests.get('{url}?{query}'.format(url=EXTERNAL_API_URL, query=query))

        if response.status_code == 200:
            return DEFAULT_ERR_MSG, json.loads(response.text)
        elif response.status_code == 400:
            return [{'error': response.text}], DEFAULT_EMPTY_RES
        else:
            return [{'error': 'Unable to get Employees from External Source'}], DEFAULT_EMPTY_RES

    def __perform_departments_request(self, department_id=None):
        if department_id is None:
            return DEFAULT_ERR_MSG, list(departments)
        elif isinstance(department_id, int):
            department = self.__get_department_by_id(department_id)
            if department is not None:
                return DEFAULT_ERR_MSG, [department]
            return DEFAULT_ERR_MSG, DEFAULT_EMPTY_RES
        else:
            return [{'error': ''}], DEFAULT_EMPTY_RES

    def __perform_offices_request(self, office_id=None):
        if office_id is None:
            return DEFAULT_ERR_MSG, list(offices)
        elif isinstance(office_id, int):
            office = self.__get_office_by_id(office_id)
            if office is not None:
                return DEFAULT_ERR_MSG, [office]
            return DEFAULT_ERR_MSG, DEFAULT_EMPTY_RES
        else:
            return [{'error': ''}], DEFAULT_EMPTY_RES

    def __call__(self, *args, **kwargs):
        err_msg, query = self.__build_query_string()

        if err_msg[0]['error'] == '':
            err_msg = self.__validate_expanded_relationships()

            if err_msg[0]['error'] != '':
                return err_msg

            perform_request_type = kwargs.pop('perform_request_type', None)

            if perform_request_type == EMPLOYEES_REQUEST:
                employee_id = kwargs.pop('employee_id', None)
                err_msg, items = self.__peform_employees_request(query=query, employee_id=employee_id)
                res = copy.copy(items)
                if err_msg[0]['error'] == '':
                    err_msg, self.managers = self.__get_all_managers(items)
            elif perform_request_type == DEPARTMENTS_REQUEST:
                department_id = kwargs.pop('department_id', None)
                err_msg, res = self.__perform_departments_request(department_id=department_id)
            elif perform_request_type == OFFICES_REQUEST:
                office_id = kwargs.pop('office_id', None)
                err_msg, res = self.__perform_offices_request(office_id=office_id)
            else:
                err_msg = [{'error': ''}]
                res = DEFAULT_EMPTY_RES

            if err_msg[0]['error'] == '':
                if self.expanded_relationships is not None:
                    return self.__expand_relationships(res)
                return res
            else:
                return err_msg

        return err_msg
