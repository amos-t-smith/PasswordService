# PasswordService
This web-service to monitor passwd and group files was developed in response to a coding challenge.
It will monitor and reload updates to files while running and provide query mechanisms based on URL parameterization described later in this page.

# Dependencies
This was developed, tested and depends on django 1.11.  
Testing was performed using python 2.7.15, and Fedora 27.

# How to Run
To run, cd to the root of this project issue the command 'python manage.py runserver'.
With the default configuration this will provide client access at 127.0.0.1:8000/pwdsvc/.

# Available URLs and Query Parameters
Available URLs provided from this web-service include:  

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
    
    name, uid, gid, comment, home  

7. To find particular groups matching a set of criteria:  
**/pwdsvc/groups/query[?name=&lt;nq&gt;][&gid=&lt;gq&gt;][&member=&lt;mq1&gt;[&member=&lt;mq2&gt;][&...]]**  
  
  The bracket notation indicates that any of the following query parameters may be supplied:

    name, gid, member (repeated).  

  Any group containing all the specified members should be returned,  
  
  
# Configuration
Settings are maintained in standard django format in PasswordService/PasswordService/settings.py.
Of particular interest in this file are the settings to configure the paths of the passwd and group files: PWDSVC_PASSWORD_FILE_PATH and PWDSVC_GROUP_FILE_PATH respectively.  
These paths default to the standard /etc/passwd and /etc/group.

# Running Unit Tests
You must first update the configuration of PWDSVC_PASSWORD_FILE_PATH and PWDSVC_GROUP_FILE_PATH to a write-able location where both files are in the same directory.

To run the unit tests, cd to the root of this project issue the command 'python manage.py test'.
