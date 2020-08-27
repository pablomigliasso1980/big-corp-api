
import copy
from urllib.parse import (
    urlparse,
    parse_qs,
    unquote
)
from mappers.constants import (
    EXPAND_ARG,
    DEFAULT_EMPTY_RES,
    DEFAULT_ERR_MSG,
    VALID_EXPANDED_RELATIONSHIPS,
    VALID_ARGS
)


class BaseMapper:
    def get_by_id(self, id):
        raise NotImplementedError()

    def get_all(self):
        raise NotImplementedError()


class ExpandableMapper():
    def __init__(self, req):
        common_args, expanded_relationships = self.__parse_query_string(req)

        self.common_args = common_args
        self.expanded_relationships = expanded_relationships

    def format_list_to_object(self, this_list):
        if len(this_list) > 0:
            return this_list[0]
        return

    def expand_relationships(self, items, relationship_getter):
        relationship_hierarchies = self.__build_relationship_hierarchies()

        for item in items:
            for hierarchy in relationship_hierarchies:
                self.__populate_relationship(this_item=item, hierarchy=hierarchy,
                                             relationship_getter=relationship_getter)

        return items

    def get_relationship_by_id(self, relationship_type, relationship_id):
        raise NotImplementedError()

    def validate_expanded_relationships(self):
        if self.expanded_relationships is not None:
            args = []
            for arg in [item.split('.') for item in self.expanded_relationships]:
                args += arg

            return self.__validate_args(args=set(args), valid_args=VALID_EXPANDED_RELATIONSHIPS)
        return DEFAULT_ERR_MSG

    def build_query_string(self):
        err_msg = self.__validate_args(args=self.common_args.keys(), valid_args=VALID_ARGS)

        if err_msg[0]['error'] == '':
            ary = []
            for key, values in self.common_args.items():
                ary += ['{arg}={value}'.format(arg=key, value=value) for value in values]
            return DEFAULT_ERR_MSG, '&'.join(ary)

        return err_msg, DEFAULT_EMPTY_RES

    def __populate_relationship(self, this_item, hierarchy, relationship_getter):
        if this_item.get(hierarchy['relationship'], None) is not None:
            if isinstance(this_item[hierarchy['relationship']], int):
                relationship = relationship_getter(relationship_type=hierarchy['relationship'],
                                                   relationship_id=this_item[hierarchy['relationship']])

                if relationship is not None:
                    this_item[hierarchy['relationship']] = copy.copy(relationship)

                    if hierarchy['children'] is not None:
                        self.__populate_relationship(this_item=this_item[hierarchy['relationship']],
                                                     hierarchy=hierarchy['children'],
                                                     relationship_getter=relationship_getter)
            elif isinstance(this_item[hierarchy['relationship']], object):
                if hierarchy['children'] is not None:
                    self.__populate_relationship(this_item=this_item[hierarchy['relationship']],
                                                 hierarchy=hierarchy['children'],
                                                 relationship_getter=relationship_getter)

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

    def __parse_query_string(self, req):
        common_args = None
        expanded_relationships = None

        if req is not None:
            common_args = parse_qs(urlparse(unquote(req.url)).query)
            expanded_relationships = common_args.pop(EXPAND_ARG, None)

        return common_args, expanded_relationships
