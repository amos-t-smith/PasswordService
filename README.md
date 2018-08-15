# PasswordService
This web-service to monitor passwd and group files was developed in response to a coding challenge.

This was developed, tested and depends on django 1.11.  
Testing was performed using python 2.7.15, and Fedora 27.

To run this system, from the root folder of this project issue the command 'python manage.py runserver'.
With the default configuration this will provide client access at 127.0.0.1:8000/pwdsvc/.

Configuration settings are maintained in standard django format in PasswordService/PasswordService/settings.py.
Of particular interest in this file are the settings to configure the paths of the passwd and group files: PWDSVC_PASSWORD_FILE_PATH and PWDSVC_GROUP_FILE_PATH respectively.  
These paths default to the standard /etc/passwd and /etc/group.

To run the unit tests issues; from the root folder of this project issue the command 'python manage.py test'.
