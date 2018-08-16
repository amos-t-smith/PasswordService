# NAME

    views

# FILE

    PasswordService/pwdsvc/views.py  

# DESCRIPTION

    This module generates responses to HTTP invocations routed to functions here-in.  
    See per function documentation for details.

# FUNCTIONS

   **groups(request)**  
   
        Purpose: Handle GET /groups;  
                 return a list of all groups on the system,  
                 a defined by /etc/group.  
        Input Parameters:  
            request - HTTP request info passed in from framework.  
        Return: HttpResponse with json representation of returned values.  
        Exceptions: N/A  
    
   **groups_by_gid(request, gid)**  
   
        Purpose: Handle GET /groups/<gid>;  
                 return a single group with <gid>. Return 404 if <gid> is not found.  
        Input Parameters:  
            request - HTTP request info passed in from framework.  
        Return: HttpResponse with json representation of returned values.  
        Exceptions: N/A  
    
   **groups_query(request)**  
   
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
        Exceptions: N/A  
    
  **search_handler(data_type_name, search_key=None, search_value=None)**
  
        Purpose: Adapt PathError and QueryError to appropriate Django error types.  
        Input Parameters:  
            data_type_name - One of the searchable types 'PasswordData' or 'GroupData'.  
            search_key - Name of searchable field for type specified Optional, default = None.  
            search_value - Value of defined field to match from data, default = None.  
        Return: HttpResponse with json representation of returned values.  
        Exceptions: Http404 on QueryError,  
                    ImproperlyConfigured on PathError  
    
  **search_results_handler(result_list)**
  
        Purpose: Raise Http404 if results are empty.  
        Input Parameters:  
            result_list - list of search reults to scan for content.  
        Return: HttpResponse  
        Exceptions: Http404 on empty results.  
    
  **search_with_params_handler(data_type_name, dict_)**
        Purpose: Adapt PathError and QueryError to appropriate Django error types.
        Input Parameters:
            data_type_name - One of the searchable types 'PasswordData' or 'GroupData'.
            dict_ - dictionary of parameters passed in to act as search keys.
        Return: HttpResponse with json representation of returned values.
        Exceptions: Http404 on QueryError,
                    ImproperlyConfigured on PathError
    
  **unique_result_expected_handler(result_list)**
        Purpose: Prune result from list to dictionary and detect multiple results
                when unique result expected.
        Input Parameters:
            result_list - list of result values to evaluate.
        Return: HttpResponse with json representation of returned values.
        Exceptions: Http404 on QueryError,
                    ImproperlyConfigured on PathError
    
  **users(request)**
        Purpose: Handle GET /users; return a list of all users on the system,
                 as defined in the /etc/passwd file.
        Input Parameters:
            request - HTTP request info passed in from framework.
        Return: HttpResponse with json representation of returned values.
        Exceptions: N/A
    
  **users_by_uid(request, uid)**
        Purpose: Handle GET /users/<uid>, return a single user with <uid>.
                 Return 404 if <uid> is not found.
        Input Parameters:
            request - HTTP request info passed in from framework.
            uid - string representation of uid value.
        Return: HttpResponse with json representation of returned values.
        Exceptions: N/A
    
  **users_query(request)**
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
        Exceptions: N/A
    
  **users_uid_groups(request, uid)**
  
        Purpose: Handle GET /users/<uid>/groups;  
                 return all the groups for a given user.  
        Input Parameters:  
            request - HTTP request info passed in from framework.  
            uid - string representation of uid value.  
        Return: HttpResponse with json representation of returned values.  
        Exceptions: N/A  

# DATA  
  
  **DATAMGR** = <pwdsvc.data.DataManager object>  
      logger = <logging.Logger object>  


