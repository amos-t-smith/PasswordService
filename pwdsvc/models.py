"""
This module provides classes to search the contents of
loaded content via database queries.
"""
from __future__ import unicode_literals
import json
from collections import OrderedDict
# Get an instance of a logger.
import logging
logger = logging.getLogger(__name__)

from pwdsvc.errors import QueryError, PathError

from django.db import models

# Create your models here.


class Account(models.Model):
    """
    This class implements the structure and functionality
    related to data loaded from passwd file.   Because this
    derives from model.Model it provides the database eqivalent
    of the data.PasswordData class.
    """

    name = models.CharField(max_length=32)
    uid = models.CharField(primary_key=True, max_length=10)
    gid = models.ForeignKey('Group')
    comment = models.TextField()
    home = models.TextField()
    shell = models.TextField()

    def __str__(self):
        """
        Purpose: Return this classes fields in json
                 string representation.
        Input N/A
        Return: string
        Exceptions: N/A.
        """
        fields = OrderedDict()
        fields['name'] = self.name
        fields['uid'] = "%d" % self.uid
        fields['gid'] = "%d" % self.gid.pk
        fields['comment'] = self.comment
        fields['home'] = self.home
        fields['shell'] = self.shell

        return json.dumps(fields, sort_keys=False)

    def to_dict(self):
        """
        Purpose: Return this classes fields in an OrderedDict.
        Input N/A
        Return: OrderedDict
        Exceptions: N/A.
        """
        fields = OrderedDict()
        fields['name'] = self.name
        fields['uid'] = self.uid
        fields['gid'] = self.gid.pk
        fields['comment'] = self.comment
        fields['home'] = self.home
        fields['shell'] = self.shell
        return fields


class Group(models.Model):
    """
    This class implements the structure and functionality
    related to data loaded from group file.   Because this
    derives from model.Model it provides the database eqivalent
    of the data.GroupdData class.
    """

    name = models.CharField(max_length=31)
    gid = models.CharField(primary_key=True, max_length=10)
    members = models.ManyToManyField(Account)

    def __str__(self):
        """
        Purpose: Return this classes fields in json
                 string representation.
        Input N/A
        Return: string
        Exceptions: N/A.
        """
        fields = OrderedDict()
        fields['name'] = self.name
        fields['gid'] = "%s" % self.gid
        members_str = ''
        for member in self.members.all():
            members_str += '%s,' % (member.name)
        fields['members'] = members_str

        return json.dumps(fields, sort_keys=False)

    def to_dict(self):
        """
        Purpose: Return this classes fields in an OrderedDict.
        Input N/A
        Return: OrderedDict
        Exceptions: N/A.
        """

        fields = OrderedDict()
        fields['name'] = self.name
        fields['gid'] = self.gid

        members_str = ''
        for member in self.members.all():
            members_str += '%s,' % (member.name)

        fields['members'] = members_str

        return fields


class DataBaseSearch(object):
    """
    Provides search methods that match data.DataManager but use
    django database functionalities internall to perform search.
    """

    def __init__(self, data_manager):
        self.data_mgr = data_manager

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

        if self.data_mgr._item_status[data_type_name] != None:
            raise self.data_mgr._item_status[data_type_name]

        member_list = []
        kwargs = {}
        for key, value in dict_.iteritems():
            logger.debug("Key: %s - Value: %s - data_type_name: %s",
                         key, value, data_type_name)

            data_key = key
            if key == 'member':
                member_list = dict_.getlist(key)
            else:
                kwargs[data_key] = value

        query_set = None

        if member_list:
            # query_set = Group.objects.filter(members__name=member_list)
            query_set = []
            for member in member_list:
                query_set_int = Group.objects.filter(members__name=member)
                if query_set != None:
                    for item in query_set_int:
                        if item not in query_set:
                            query_set.append(item)

            if query_set and kwargs:
                query_set = query_set_int.filter(**kwargs)

        else:
            if data_type_name == 'PasswordData':
                query_set = Account.objects.filter(**kwargs)
            elif data_type_name == 'GroupData':
                query_set = Group.objects.filter(**kwargs)

        for item in query_set:
            new_data = self.data_mgr.get_class(data_type_name)
            new_data.from_dict(item.to_dict())
            ret.append(new_data)

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

        if self.data_mgr._item_status[data_type_name] != None:
            raise self.data_mgr._item_status[data_type_name]

        logger.debug('Search Key %s', search_key)
        if search_key != None:
            logger.debug('Searching type: %s', data_type_name)
            lookup_dict = self.data_mgr._item_lookup[data_type_name]

            if search_key in lookup_dict:
                kwargs = {}
                kwargs[search_key] = search_value

                query_set = None
                if data_type_name == 'PasswordData':
                    query_set = Account.objects.filter(**kwargs)
                elif data_type_name == 'GroupData':
                    query_set = Group.objects.filter(**kwargs)

                if query_set:
                    for item in query_set:
                        new_data = self.data_mgr.get_class(data_type_name)
                        new_data.from_dict(item.to_dict())
                        ret.append(new_data)

            else:
                error_msg = 'search_key not found: %s' % (search_key)
                logger.error(error_msg)
                raise QueryError(error_msg)
        else:
            query_set = None
            if data_type_name == 'PasswordData':
                query_set = Account.objects.all()
            elif data_type_name == 'GroupData':
                query_set = Group.objects.all()

            if query_set:
                for item in query_set:
                    new_data = self.data_mgr.get_class(data_type_name)
                    new_data.from_dict(item.to_dict())
                    ret.append(new_data)

        return ret
