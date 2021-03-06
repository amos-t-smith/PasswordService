# PasswordService
This web-service to monitor passwd and group files was developed in response to a coding challenge.
It will monitor and reload updates to files while running and provide query mechanisms based on URL parameterization described later in this page.

# Dependencies
This was developed, tested and depends on django 1.11.  
Testing was performed using python 2.7.15 on Fedora 27.

# How to Run
To run, cd to the root of this project issue the command 'python manage.py runserver'.
With the default configuration this will provide client access at 127.0.0.1:8000/pwdsvc/.

# Available URLs and Query Parameters
Available URLs provided from this web-service include the following.

1. To show all users in passwd file:  
**/pwdsvc/users**  

2. To search for particular user by uid:  
**/pwdsvc/users/&lt;uid&gt;**  

3. To search for groups that a user is member of:  
**/pwdsvc/users/&lt;uid&gt;/groups**  

4. To show all groups in group file:  
**/pwdsvc/groups**  

5. To search for particular group by gid:  
**/pwdsvc/groups/&lt;gid&gt;**  

6. To find particular users matching a set of criteria:  
**/pwdsvc/users/query[?name=&lt;nq>][&amp;uid=&lt;uq&gt;][&amp;gid=&lt;gq&gt;][&amp;comment=&lt;cq&gt;][&amp;home=&lt;q&gt;][&shell=&lt;sq&gt;]**  

  The bracket notation indicates that any of the following query parameters may be supplied:  
   
   - name
   - uid
   - gid
   - comment
   - home  

7. To find particular groups matching a set of criteria:  
**/pwdsvc/groups/query[?name=&lt;nq&gt;][&gid=&lt;gq&gt;][&member=&lt;mq1&gt;[&member=&lt;mq2&gt;][&...]]**  
  
  The bracket notation indicates that any of the following query parameters may be supplied:
  
   - name
   - gid
   - member (repeated).  

  Any group containing all the specified members should be returned,  

__*Reference the following links for detailed description of functionality implementing these URLs.*__  
1. [VIEWS](VIEWS.md)  
2. [DATA](DATA.md)
  
# Configuration
Settings are maintained in standard django format in PasswordService/PasswordService/settings.py.
Of particular interest in this file are the settings to configure the paths of the passwd and group files:   __*PWDSVC_PASSWORD_FILE_PATH*__ - path to passwd file, defaults to /etc/passwd.
__*PWDSVC_GROUP_FILE_PATH*__ - path to group file, defaults to /etc/group.

# Running Unit Tests
You must first update the configuration of PWDSVC_PASSWORD_FILE_PATH and PWDSVC_GROUP_FILE_PATH to a write-able location where both files are in the same directory.

To run the unit tests, cd to the root of this project issue the command 'python manage.py test'.

# Notes on Approach and Known Limitations
The coding challenge called for "production quality" by the developers definition; which I'm considering to mean documented in a standard format (pydoc), statically analyzed (pylint), and unit tested enough to identify potential issues to consider in production integration.  In a more typical engineering process I would expect "production quality" to include design artifacts such as class and sequence diagrams, consideration of SLA requirements in unit tests, Product Owner input, and analysis of adherence to secure coding standards.

The approach I've taken is relatively standard Django app except for the ability to bypass the django.model/database backed search when the PWDSVC_SEARCH setting is not 'DataBaseSearch'.  Future versions will include unit test to compare performance between relational database approach and alternal dictionary based implementation in pwdsvc.data.DataMgr.

Currently identified limitations include 1) a sub-second lower-bound in handling file updates, and 2) a local system virtual memory constraint on the size of files that can be successfully loaded into the pwdsvc.data.DataMgr module when not using a database.
