"""
This module provides classes to load the passwd and group files,
search the contents of loaded content, monitor and reload files on
file change while running.
"""

import os
import os.path
import logging
import json
from collections import OrderedDict
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from django.conf import settings

# Get an instance of a logger.
logger = logging.getLogger(__name__)

class QueryError(RuntimeError):
    """
    This class when raised provides conveys that an exceptional
    situation occurred while trying to process a query.
    """
    pass


class PathError(RuntimeError):
    """
    This class when raised conveys that an exceptional
    situation occurred while trying load the passwd
    or group files respectively; i.e. bad path to file.
    """
    pass


class BaseDataType(object):
    """
    This class implements the common structure and functionality
    related to data loaded from either passwd or group files.
    """

    def __init__(self, field_names):
        self._fields = OrderedDict()

        for name in field_names:
            self._fields[name] = ''

    def get_field(self, key):
        """
        Purpose: Search for field by key and return string value.
        Input Parameters:
            key - name of field to search.
        Return: Falue of specified field, None if not found.
        Exceptions: N/A"""
        ret = None

        if key in self._fields:
            ret = self._fields[key]

        return ret

    def __repr__(self):
        """
        Purpose: Return json representation of fields as string.
        Input Parameters: N/A
        Return: json encoded value of _fields as a string.
        Exceptions: N/A"""
        out_dict = {}
        for key, val in self._fields.items():
            out_dict[key] = val

        return json.dumps(self._fields, sort_keys=False)

    def compare_fields(self, fields):
        """
        Purpose: Compare the _fields in this instance to fields passed in.
        Input Parameters: fields, dictionary of values to compare against.
        Return: True if all fields match.
                True if field name is members and all fields
                in input parameter are subset of _fields[members].
                Other wise False.
        Exceptions: QueryError if unsupported fields are specified."""
        ret = True

        for key, val in fields.items():
            if key == 'member':
                query_members = fields.getlist(key)
                data_key = 'members'
                data_members = self._fields[data_key].split(',')

                # So long as the queried members exist it's to be considered a match,
                # even if there are additional members not in the query.
                for q_member in query_members:
                    if q_member not in data_members:
                        ret = False
                        break

            else:
                if key not in self._fields:
                    errmsg = 'Unsupported key for this type: %s' % (key)
                    logger.debug(errmsg)
                    raise QueryError(errmsg)

                if self._fields[key] != val:
                    ret = False
                    break

        return ret

    def prepare_search(self, dict_):
        """
        Purpose: Loads dictionaries to support lookup of specified values.
        Input Parameters: dict_, dictionary of values to iterate and load.
        Return: N/A.
        Exceptions: N/A."""

        if(len(dict_)) == 0:
            # initialize lookup table if empty
            for key, val in self._fields.items():
                dict_[key] = {}

        # update lookup table with my current values
        for key, val in self._fields.items():
            if key == 'members':
                # Split members csv format and register
                # each name to this instance.
                for subval in val.split(','):
                    if subval not in dict_[key]:
                        # lazy initialize list
                        dict_[key][subval] = []

                    # add user name to list
                    dict_[key][subval].append(self)
            else:
                if val not in dict_[key]:
                    # lazy initialize of lookup
                    dict_[key][val] = []

                # Register this instance as value to return
                # from search of this field type/value combo.
                dict_[key][val].append(self)


class PasswordData(BaseDataType):
    """
    This class implements the structure and functionality
    related to data loaded from passwd file.
    """

    def __init__(self):
        field_names = ['name', 'uid', 'gid', 'comment', 'home', 'shell']
        BaseDataType.__init__(self, field_names)
        self.source_field_size = 7

    def load_from_list(self, list_):
        """
        Purpose: Load fields from list of values passed in.
        Input Parameters: list_, list of values in order saved in passwd file.
        Return: N/A.
        Exceptions: N/A."""

        if len(list_) == 7:
            self._fields['name'] = list_[0]
            self._fields['uid'] = list_[2]
            self._fields['gid'] = list_[3]
            self._fields['comment'] = list_[4]
            self._fields['home'] = list_[5]
            self._fields['shell'] = list_[6]
        else:
            raise RuntimeError('Invalid User Data: %s' % (list_))


class GroupData(BaseDataType):
    """
    This class implements the structure and functionality
    related to data loaded from group file.
    """

    def __init__(self):
        self.source_field_size = 4
        BaseDataType.__init__(self, ['name', 'gid', 'members'])

    def load_from_list(self, list_):
        """
        Purpose: Load fields from list of values passed in.
        Input Parameters: list_, list of values in order saved in group file.
        Return: N/A.
        Exceptions: N/A."""

        if len(list_) == 4:
            self._fields['name'] = list_[0]
            self._fields['gid'] = list_[2]
            self._fields['members'] = list_[3]
        else:
            raise RuntimeError('Invalid Group Data: %s' % (list_))


class DataFileEventHandler(PatternMatchingEventHandler):
    """
    This class handles file change events on passwd or group files.
    """

    def __init__(self, patterns):
        PatternMatchingEventHandler.__init__(self, patterns)
        self._data_mgr = None
        self._data_type = None
        self._file_path = ''

    def init_callback(self, data_mgr, file_path, data_type):
        """
        Purpose: Initializes callback so that this class can
                 reload the data in DataManager.
        Input Parameters:
            data_mgr - instance of data_mgr.
            file_path - path to file to watch.
            data_type - type of data being watched (Password or Group).
        Return: N/A.
        Exceptions: N/A."""

        logger.debug('Callback initialized: %s', file_path)
        self._data_mgr = data_mgr
        self._data_type = data_type
        self._file_path = file_path

    def on_modified(self, event):
        """
        Purpose: Receives notification of file change and calls
                on DataManager instance to reload.
        Input Parameters:
            event - type of filesystem event.
        Return: N/A.
        Exceptions: N/A."""
        logger.debug("on_modified event received: %s", event)

        if event.src_path == self._file_path:
           logger.debug("Path changed: %s", self._file_path)
        else:
           logger.debug('Not the path being observed.')
           return

        if self._data_mgr != None:
            try:                
                self._data_mgr.reload_datatype(self._data_type)
            except RuntimeError, runtime_error:
                logger.error(runtime_error)

PWD_TYPENAME = PasswordData.__name__
GRP_TYPENAME = GroupData.__name__

class DataManager(object):
    """
    This class handles loading of passwd and group files and
    provides methods for searching the data loaded.
    """

    def __init__(self):
        self._file_path = {}
        self._file_path[PWD_TYPENAME] = settings.PWDSVC_PASSWORD_FILE_PATH
        self._file_path[GRP_TYPENAME] = settings.PWDSVC_GROUP_FILE_PATH

        # Per type dictionary of lists that hold all data loaded.
        self._item_list = {}

        # Per type dictionary of dictionaries that allows for search of data
        # without a database intance.
        self._item_lookup = {}

        # Per type instances of server error codes raised on internal error
        # such as misconfigured settings file (i.e. invalid passowrd file).
        self._item_status = {}

        # Per type instances of watchdog to monitor url for change while running.
        self._item_watch = {}

        self.init_data_type(PWD_TYPENAME)
        self.init_data_type(GRP_TYPENAME)

        self.load_data()

    def init_data_type(self, data_type_name):
        """
        Purpose: Initialize dictionaries indexed by datatype to support search.
        Input Parameters:
            data_type_name - name of data type to use as index.
        Return: N/A.
        Exceptions: N/A."""
        self._item_lookup[data_type_name] = {}
        self._item_status[data_type_name] = None
        self._item_list[data_type_name] = []
        self._item_watch[data_type_name] = None

    def search_with_params(self, data_type_name, dict_):
        """
        Purpose: Given data type name and dictionary of params
                 find a list of matching BaseDataType instances.
        Input Parameters:
            data_type_name - name of data type to use as index.
            dict_ - OrderedDict containing parameters to use as
                    search criteria.
        Return: list of BaseDataType (or subclassed) instances.
        Exceptions: N/A."""
        ret = []

        if self._item_status[data_type_name] != None:
            raise self._item_status[data_type_name]

        for key, value in dict_.iteritems():
            logger.debug("Key: %s - Value: %s - data_type_name: %s",
                         key, value, data_type_name)

            data_key = key
            if key == 'member':
                data_key = 'members'

            new_matches = self.search(data_type_name, data_key, value)

            if new_matches != None:
                logger.debug(
                    'Found a potential match on: %s = %s.', key, value)

                for match in new_matches:
                    # found a candidate
                    if match in ret:
                        # already in results, don't add again
                        continue

                    # compare all fields in query
                    if match.compare_fields(dict_):
                        # all fields match, add to results
                        ret.append(match)
                    else:
                        logger.debug('Failed compare: %s - %s.',
                                     match, dict_)
                        continue

        return ret

    def search(self, data_type_name, search_key=None, search_value=None):
        """
        Purpose: Given data type name, key, and value;
                 find a list of matching BaseDataType instances.
        Input Parameters:
            data_type_name - name of data type to use as index.
            search_key - field name to use as search criteria.
            search_value - value to use as search criteria for specified key.
        Return: list of BaseDataType (or subclassed) instances.
        Exceptions: N/A."""
        ret = []

        if self._item_status[data_type_name] != None:
            raise self._item_status[data_type_name]

        logger.debug('Search Key %s', search_key)
        if search_key != None:
            logger.debug('Searching type: %s', data_type_name)
            lookup_dict = self._item_lookup[data_type_name]

            if search_key in lookup_dict:
                lookup = lookup_dict[search_key]

                if search_value in lookup:
                    ret = lookup[search_value]
                    logger.debug('Found items: %s', ret)
                else:
                    logger.debug('search_value not found: %s', search_value)

            else:
                error_msg = 'search_key not found: %s' % (search_key)
                logger.error(error_msg)
                raise QueryError(error_msg)
        else:
            ret = self._item_list[data_type_name]

        return ret

    def start_watchdog(self, data_type):
        """
        Purpose: Given data type name; start a watchdog observer
                 to monitor for file changes at configured path.
        Input Parameters:
            data_type_name - data type to use as index.
        Return: N/A
        Exceptions: N/A."""

        data_type_name = data_type.__name__
        path = self._file_path[data_type_name]

        # observer already running, close it down.
        if data_type_name in self._item_watch:
            observer = self._item_watch[data_type_name]
            if observer != None:
                observer.join()

        # create new watchdog and register by type
        observer = Observer()
        self._item_watch[data_type_name] = observer

        patterns = [path]
        event_handler = DataFileEventHandler(patterns=patterns)
        event_handler.init_callback(self, path, data_type)
        observer.schedule(event_handler, os.path.split(path)
                          [0], recursive=False)
        observer.start()

    def load_data_by_type(self, data_type):
        """
        Purpose: Given data type name; start a watchdog observer
                 to monitor for file changes at configured path.
        Input Parameters:
            data_type_name - data type to use as index.
        Return: N/A
        Exceptions: N/A."""

        data_type_name = data_type.__name__
        path = self._file_path[data_type_name]
        lines = []

        try:
            logger.debug('Loading: %s', path)
            with open(path) as data_file:
                lines = data_file.readlines()
        except RuntimeError, runtime_error:
            self._item_status[data_type_name] = PathError(
                'Unabled to open path: "%s", on error: %s' % (path, runtime_error))
            # Site will stay up but data will be empty on queries
            # for this type will return PathError exception
            # with notice about invalid path value.
            logger.error(runtime_error)

        if len(lines) > 0:
            item_lookup = self._item_lookup[data_type_name]

            for line in lines:
                new_item = data_type()

                line_vals = line.replace('\n', '').split(':')

                if len(line_vals) == new_item.source_field_size:
                    new_item.load_from_list(line_vals)
                    self._item_list[data_type_name].append(new_item)
                else:
                    logger.error(
                        'Data omitted as it appears to be malformed: %s.', line)

                # this builds out dictionaries to support search of data.
                new_item.prepare_search(item_lookup)

    def reload_datatype(self, data_type):
        """
        Purpose: Given data type name; reload source path.
        Input Parameters:
            data_type - data type to use as index.
        Return: N/A
        Exceptions: N/A."""
        data_type_name = data_type.__name__
        logger.debug('Reloading type: %s.', data_type_name)

        self.init_data_type(data_type_name)
        self.load_data_by_type(data_type)

    def load_data(self):
        """
        Purpose: Load all types of data and start monitoring files.
        Input Parameters: N/A
        Return: N/A
        Exceptions: N/A."""
        logger.debug('Start loading data.')
        self.load_data_by_type(PasswordData)
        self.load_data_by_type(GroupData)

        self.start_watchdog(PasswordData)
        self.start_watchdog(GroupData)
        logger.debug('Done loading data.')
