""" This module provides unit test coverage for
    the PasswordService project. 
"""
import logging
import os
import os.path
import time
from django.test import TestCase
from django.conf import settings

# Test Views
from django.urls import reverse
from pwdsvc.data import PWD_TYPENAME, GRP_TYPENAME, DataManager

logger = logging.getLogger(__name__)

# To increase this just need alternate name generation scheme.
MAX_USER_SIZE = 25

class UserData(object):
    """ 
        Provides mechanism to write known values into configured location paths
        so that the expected outputs can be programattically compared to the
        actual results in assert statements.
    """
    def __init__(self):
        self.user_names = []
        for i in range(MAX_USER_SIZE):
            new_name = ''
            for j in range(4):
                new_name = new_name + chr(65+i)

            self.user_names.append(new_name)

        self.pwd_data = []
        self.grp_data = []

        pwd_path = settings.PWDSVC_PASSWORD_FILE_PATH
        grp_path = settings.PWDSVC_GROUP_FILE_PATH

        pwd_dir = os.path.split(pwd_path)[0]
        grp_dir = os.path.split(grp_path)[0]

        if grp_dir != pwd_dir:
            raise RuntimeError('Directory for passwd and group file must be same for unit tests.')

        if not os.path.isdir(pwd_dir):
            os.mkdir(pwd_dir)

        self.pwd_path = pwd_path
        self.grp_path = grp_path

    def write_data(self, size):
        """Write rows of user and group data into files.
           The number of rows written is defined by input
           parameter size.
        """
        pwd_data = self.pwd_data
        grp_data = self.grp_data

        # Passwd data.
        pwd_data = []
        for i in range(size):
            name = self.user_names[i]
            uid = '%d' % (100 + i)
            gid = '%d' % (1000 + i)
            pwd_data.append('%s:x:%s:%s:%s:/home/%s:/bin/bash\n' % (name, uid, gid, name, name))
        self.pwd_data = pwd_data

        # Group data.
        grp_data = []
        grp_data.append('root:x:0:\n')
        grp_data.append('bin:x:1:\n')
        grp_data.append('daemon:x:2:\n')

        members = ''
        for i in range(size):
            name = self.user_names[i]
            gid = '%d' % (1000 + i)
            grp_data.append('%s:x:%s:\n' % (name, gid))
            members = members + '%s,' % (name)

        grp_data.append('test_users:x:999:%s\n' % (members))

        self.grp_data = grp_data

        if size > MAX_USER_SIZE:
            raise RuntimeError('User count cannot exceed: %d' % (MAX_USER_SIZE))

        with open(self.pwd_path, 'w+') as pwd_file:
            pwd_file.writelines(pwd_data)

        with open(self.grp_path, 'w+') as grp_file:
            grp_file.writelines(grp_data)

USER_DATA = UserData()


class FileUpdate(TestCase):
    """Test loading data and custom location and see if it reloads when changed."""
    def setUp(self):
        # Write initial test data.
        USER_DATA.write_data(3)

        # Load the data manager.
        self.data_mgr = DataManager()

    def test_data_loaded(self):
        """Check to see if expected pwd data is initially loaded."""
        users = self.data_mgr.search(PWD_TYPENAME)
        self.assertEqual(len(users), len(USER_DATA.pwd_data))

        groups = self.data_mgr.search(GRP_TYPENAME)
        self.assertEqual(len(groups), len(USER_DATA.grp_data))
        logging.info('Finished test_data_loaded.')

    def test_data_reloaded(self):
        """Check to see if expected data is loaded after update of files."""
        #for i in range(5, MAX_USER_SIZE, 5):
        for i in range(MAX_USER_SIZE - 5, MAX_USER_SIZE, 5):
            USER_DATA.write_data(i)

            # Passes on test system consistently with a 1 second sleep
            # between file updates.  Update failure begins to increase
            # significantly at around 0.8 seconds.
            #
            # This seems reasonable given the purpose of this
            # update mechanism and nature of task.
            time.sleep(1.0)

            users = self.data_mgr.search(PWD_TYPENAME)
            self.assertEqual(len(users), len(USER_DATA.pwd_data))

            groups = self.data_mgr.search(GRP_TYPENAME)
            self.assertEqual(len(groups), len(USER_DATA.grp_data))

        logging.info('Finished test_data_reloaded.')

class ViewTests(TestCase):
    """Test loading views."""

    def setUp(self):
        """Re-initialize data to known state."""
        USER_DATA.write_data(3)

    def test_users(self):
        """Test loading GET /users."""
        response = self.client.get(reverse('users'))
        self.assertEqual(response.status_code, 200)

    def test_groups(self):
        """Test loading the /groups."""
        response = self.client.get(reverse('groups'))
        self.assertEqual(response.status_code, 200)

    def test_group_gid(self):
        """Test loading GET /group/<gid>."""
        for grp_data in USER_DATA.grp_data:
            gid = grp_data.split(':')[2]
            url = reverse('groups_by_gid', args=[gid])
            self.assertEqual(url, unicode('/pwdsvc/groups/%s' % (gid)))
            response = self.client.get(url)

            self.assertEqual(response.status_code, 200)

        # negative test should 404
        bad_gid = 9999
        url = reverse('groups_by_gid', args=[bad_gid])
        self.assertEqual(url, unicode('/pwdsvc/groups/%s' % (bad_gid)))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)  

    def test_users_params(self):
        """Test loading GET /users/query."""
        url = reverse('users_query')
        self.assertEqual(url, unicode('/pwdsvc/users/query'))

        for pwd_data in USER_DATA.pwd_data:
            pwd_data_parts = pwd_data.split(':')
            name = pwd_data_parts[0]
            uid = pwd_data_parts[2]
            gid = pwd_data_parts[3]       
            
            name_query = url + '?name=%s' % (name)
            response = self.client.get(name_query)
            self.assertEqual(response.status_code, 200)

            uid_query = url + '?uid=%s' % (uid)
            response = self.client.get(uid_query)
            self.assertEqual(response.status_code, 200)

            gid_query = url + '?gid=%s' % (gid)
            response = self.client.get(gid_query)
            self.assertEqual(response.status_code, 200)            

            #invalid_query = url + '?not_a_param=%s' % (name)
            #response = self.client.get(invalid_query)
            #self.assertEqual(response.status_code, 404)

    def test_grp_params(self):
        """Test loading the GET /groups/query."""
        url = reverse('groups_query')
        self.assertEqual(url, unicode('/pwdsvc/groups/query'))

        for grp_data in USER_DATA.grp_data:
            grp_data_parts = grp_data.split(':')
            name = grp_data_parts[0]
            gid = grp_data_parts[2]
            
            name_query = url + '?name=%s' % (name)
            response = self.client.get(name_query)
            self.assertEqual(response.status_code, 200)

            gid_query = url + '?gid=%s' % (gid)
            response = self.client.get(gid_query)
            self.assertEqual(response.status_code, 200)

        name_a = 'AAAA'
        grp_members_query = url + '?member=%s' % (name_a)       
        response = self.client.get(grp_members_query)
        self.assertEqual(response.status_code, 200)

        name_b = 'BBBB'
        grp_members_query = url + '?member=%s&member=%s' % (name_a, name_b)       
        response = self.client.get(grp_members_query)
        self.assertEqual(response.status_code, 200)

        gid = '999'
        grp_members_query = url + '?member=%s&member=%s&gid=%s' % (name_a, name_b, gid)
        response = self.client.get(grp_members_query)
        self.assertEqual(response.status_code, 200)        

        invalid_value_query = url + '?name=qwerty'
        response = self.client.get(invalid_value_query)
        self.assertEqual(response.status_code, 404)


    def test_user_uid_groups(self):
        """Test loading GET users/<uid>/groups. """
        for pwd_data in USER_DATA.pwd_data:
            pwd_data_parts = pwd_data.split(':')
            #name = pwd_data_parts[0]
            uid = pwd_data_parts[2]

            url = reverse('users_uid_groups', args=[uid])
            self.assertEqual(url, unicode('/pwdsvc/users/%s/groups' % (uid)))
            response = self.client.get(url)

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, 'test_users')

    def test_user_uid(self):
        """Test loading GET /users/<uid>."""
        for pwd_data in USER_DATA.pwd_data:
            pwd_data_parts = pwd_data.split(':')

            name = pwd_data_parts[0]
            uid = pwd_data_parts[2]

            url = reverse('users_by_uid', args=[uid])
            self.assertEqual(url, unicode('/pwdsvc/users/%s' % (uid)))
            response = self.client.get(url)

            self.assertEqual(response.status_code, 200)
            self.assertContains(response, name)
            self.assertNotContains(response, 'DDDD') #one name past last loaded

        # negative test should 404
        bad_uid = 9999
        url = reverse('users_by_uid', args=[bad_uid])
        self.assertEqual(url, unicode('/pwdsvc/users/%s' % (bad_uid)))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

