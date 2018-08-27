""" This module generates responses to HTTP invocations routed to functions here-in.
    See per function documentation for details."""
import logging
from django.http import HttpResponse
from django.http import Http404
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings
from pwdsvc.data import QueryError, PathError, PasswordData, GroupData, DataManager
from pwdsvc.models import Group, Account, DataBaseSearch

logger = logging.getLogger(__name__)

# Load an instance of the file monitor and search engine.
DATAMGR = DataManager()

def search_results_handler(result_list):
    """
    Purpose: Raise Http404 if results are empty.
    Input Parameters:
        result_list - list of search reults to scan for content.
    Return: HttpResponse
    Exceptions: Http404 on empty results."""

    if not result_list:
        raise Http404('No results found.')
    else:
        return HttpResponse("%s" % result_list)


def search_handler(data_type_name, search_key=None, search_value=None):
    """
    Purpose: Adapt PathError and QueryError to appropriate Django error types.
    Input Parameters:
        data_type_name - One of the searchable types 'PasswordData' or 'GroupData'.
        search_key - Name of searchable field for type specified Optional, default = None.
        search_value - Value of defined field to match from data, default = None.
    Return: HttpResponse with json representation of returned values.
    Exceptions: Http404 on QueryError,
                ImproperlyConfigured on PathError """

    result_list = []
    try:
        search_type = settings.PWDSVC_SEARCH
        if search_type == 'DataBaseSearch':
            db_search = DataBaseSearch(DATAMGR)
            result_list = db_search.search(data_type_name, search_key, search_value)
        else:
            result_list = DATAMGR.search(data_type_name, search_key, search_value)
    except PathError, path_error:
        raise ImproperlyConfigured(path_error)
    except QueryError, query_error:
        raise Http404(query_error)

    if not result_list:
        raise Http404('No results.')

    return result_list


def search_with_params_handler(data_type_name, dict_):
    """
    Purpose: Adapt PathError and QueryError to appropriate Django error types.
    Input Parameters:
        data_type_name - One of the searchable types 'PasswordData' or 'GroupData'.
        dict_ - dictionary of parameters passed in to act as search keys.
    Return: HttpResponse with json representation of returned values.
    Exceptions: Http404 on QueryError,
                ImproperlyConfigured on PathError """
    result_list = []

    try:
        search_type = settings.PWDSVC_SEARCH
        if search_type == 'DataBaseSearch':
            db_search = DataBaseSearch(DATAMGR)
            result_list = db_search.search_with_params(data_type_name, dict_)
        else:
            result_list = DATAMGR.search_with_params(data_type_name, dict_)

    except PathError, path_error:
        raise ImproperlyConfigured(path_error)
    except QueryError, query_error:
        raise Http404(query_error)

    return result_list


def unique_result_expected_handler(result_list):
    """
    Purpose: Prune result from list to dictionary and detect multiple results
            when unique result expected.
    Input Parameters:
        result_list - list of result values to evaluate.
    Return: HttpResponse with json representation of returned values.
    Exceptions: Http404 on QueryError,
                ImproperlyConfigured on PathError """
    if len(result_list) > 1:
        raise Http404(
            'Invalid number of results for this query: %s.' % (result_list))
    else:
        # prune to first result
        result_list = result_list[0]

    return HttpResponse(result_list)


def users(request):
    """
    Purpose: Handle GET /users; return a list of all users on the system,
             as defined in the /etc/passwd file.
    Input Parameters:
        request - HTTP request info passed in from framework.
    Return: HttpResponse with json representation of returned values.
    Exceptions: N/A """

    logger.debug('Request routed to users: %s', request)
    result_list = search_handler(PasswordData.__name__)

    return search_results_handler(result_list)


def users_by_uid(request, uid):
    """
    Purpose: Handle GET /users/<uid>, return a single user with <uid>.
             Return 404 if <uid> is not found.
    Input Parameters:
        request - HTTP request info passed in from framework.
        uid - string representation of uid value.
    Return: HttpResponse with json representation of returned values.
    Exceptions: N/A """
    logger.debug('Request routed to user_by_uid: %s', request)
    result_list = search_handler(PasswordData.__name__, 'uid', uid)
    return unique_result_expected_handler(result_list)


def users_uid_groups(request, uid):
    """
    Purpose: Handle GET /users/<uid>/groups;
             return all the groups for a given user.
    Input Parameters:
        request - HTTP request info passed in from framework.
        uid - string representation of uid value.
    Return: HttpResponse with json representation of returned values.
    Exceptions: N/A """

    logger.debug('Request routed to users_uid_groups: %s', request)
    # This will throw 404 if no user by uid finds result.
    user = search_handler(PasswordData.__name__, 'uid', uid)

    name = user[0].get_field('name')
    gid = user[0].get_field('gid')

    # Joining matches of search on user name and gid to group information.
    result_list = DATAMGR.search(GroupData.__name__, 'gid', gid)
    result_list += DATAMGR.search(GroupData.__name__, 'members', name)

    return search_results_handler(result_list)


def users_query(request):
    """
    Purpose: Handle GET
            /users/query[?name=<nq>][&uid=<uq>][&gid=<gq>][&comment=<cq>][&home=<hq>][&shell=<sq>]
             Return a list of users matching all of the specified query fields.
            The bracket notation indicates that any of the
            following query parameters may be supplied:
            -name
            -uid
            -gid
            -comment
            -home
    Input Parameters:
        request - HTTP request info passed in from framework;
                namely including dictionary of parameters.
    Return: HttpResponse with json representation of returned values.
    Exceptions: N/A """
    logger.debug('Routed to users_query %s.', request)
    result_list = search_with_params_handler(
        PasswordData.__name__, request.GET)
    return search_results_handler(result_list)


def groups(request):
    """
    Purpose: Handle GET /groups;
             return a list of all groups on the system,
             a defined by /etc/group.
    Input Parameters:
        request - HTTP request info passed in from framework.
    Return: HttpResponse with json representation of returned values.
    Exceptions: N/A """
    logger.debug('Routed to groups %s.', request)
    result_list = search_handler(GroupData.__name__)

    return search_results_handler(result_list)


def groups_by_gid(request, gid):
    """
    Purpose: Handle GET /groups/<gid>;
             return a single group with <gid>. Return 404 if <gid> is not found.
    Input Parameters:
        request - HTTP request info passed in from framework.
    Return: HttpResponse with json representation of returned values.
    Exceptions: N/A """
    logger.debug('Routed to group_by_gid: %s.', request)
    result_list = search_handler(GroupData.__name__, 'gid', gid)
    return unique_result_expected_handler(result_list)


def groups_query(request):
    """
    Purpose: Handle GET
                    /groups/query
                    [?name=<nq>][&gid=<gq>][&member=<mq1>[&member=<mq2>][&...]]
             Return a list of groups matching all of the specified query fields.
             The bracket notation indicates that any of the following
             query parameters may be supplied:
            -name
            -gid
            -member (repeated)

            Any group containing all the specified members should be returned,
            i.e. when query members are a subset of group members.
    Input Parameters:
        request - HTTP request info passed in from framework;
                  namely including dictionary of parameters.
    Return: HttpResponse with json representation of returned values.
    Exceptions: N/A """

    logger.debug('Routed to groups_query %s', request.GET)
    result_list = search_with_params_handler(GroupData.__name__, request.GET)
    return search_results_handler(result_list)
