# NAME

    data

# FILE

    PasswordService/pwdsvc/data.py

# DESCRIPTION

    This module provides classes to load the passwd and group files,  
    search the contents of loaded content, monitor and reload files on  
    file change while running.  

# CLASSES

    __builtin__.object  
        BaseDataType  
            GroupData  
            PasswordData  
        DataManager  
    exceptions.RuntimeError(exceptions.StandardError)  
        PathError  
        QueryError  
    watchdog.events.PatternMatchingEventHandler(watchdog.events.FileSystemEventHandler)  
        DataFileEventHandler  
    
   **class BaseDataType(__builtin__.object)**  

     |  This class implements the common structure and functionality  
     |  related to data loaded from either passwd or group files.  
     |  
     |  Methods defined here:  
     |  
     
   **__init__(self, field_names)**   
   
     |  
     
   **__repr__(self)**      
   
     |      Purpose: Return json representation of fields as string.  
     |      Input Parameters: N/A  
     |      Return: json encoded value of _fields as a string.  
     |      Exceptions: N/A  
     |  
     
   **compare_fields(self, fields)**  
   
     |      Purpose: Compare the _fields in this instance to fields passed in.
     |      Input Parameters: fields, dictionary of values to compare against.
     |      Return: True if all fields match.
     |              True if field name is members and all fields
     |              in input parameter are subset of _fields[members].
     |              Other wise False.
     |      Exceptions: QueryError if unsupported fields are specified.
     |  
     
   **get_field(self, key)**  
   
     |      Purpose: Search for field by key and return string value.
     |      Input Parameters:
     |          key - name of field to search.
     |      Return: Falue of specified field, None if not found.
     |      Exceptions: N/A
     |  
     
   **prepare_search(self, dict_)**  
   
     |      Purpose: Loads dictionaries to support lookup of specified values.
     |      Input Parameters: dict_, dictionary of values to iterate and load.
     |      Return: N/A.
     |      Exceptions: N/A.
     |  
    
   **class DataFileEventHandler(watchdog.events.PatternMatchingEventHandler)**  
   
     |  This class handles file change events on passwd or group files.
     |  
     |  Method resolution order:
     |      DataFileEventHandler
     |      watchdog.events.PatternMatchingEventHandler
     |      watchdog.events.FileSystemEventHandler
     |      __builtin__.object
     |  
     |  Methods defined here:
     |  
   **__init__(self, patterns)**  
   
     |  
     
   **init_callback(self, data_mgr, file_path, data_type)**  
   
     |      Purpose: Initializes callback so that this class can
     |               reload the data in DataManager.
     |      Input Parameters:
     |          data_mgr - instance of data_mgr.
     |          file_path - path to file to watch.
     |          data_type - type of data being watched (Password or Group).
     |      Return: N/A.
     |      Exceptions: N/A.
     |  
     
   **on_modified(self, event)**  
   
     |      Purpose: Receives notification of file change and calls
     |              on DataManager instance to reload.
     |      Input Parameters:
     |          event - type of filesystem event.
     |      Return: N/A.
     |      Exceptions: N/A.
    
   **class DataManager(__builtin__.object)**  

     |  This class handles loading of passwd and group files and
     |  provides methods for searching the data loaded.
     |  
     |  Methods defined here:
     |  
   **__init__(self)**  
   
     |  
     
   **init_data_type(self, data_type_name)**  
   
     |      Purpose: Initialize dictionaries indexed by datatype to support search.
     |      Input Parameters:
     |          data_type_name - name of data type to use as index.
     |      Return: N/A.
     |      Exceptions: N/A.
     |  
     
   **load_data(self)**  
   
     |      Purpose: Load all types of data and start monitoring files.
     |      Input Parameters: N/A
     |      Return: N/A
     |      Exceptions: N/A.
     |  
     
   **load_data_by_type(self, data_type)**  
   
     |      Purpose: Given data type name; start a watchdog observer
     |               to monitor for file changes at configured path.
     |      Input Parameters:
     |          data_type_name - data type to use as index.
     |      Return: N/A
     |      Exceptions: N/A.
     |  
     |  **reload_datatype(self, data_type) **  
     |      Purpose: Given data type name; reload source path.
     |      Input Parameters:
     |          data_type - data type to use as index.
     |      Return: N/A
     |      Exceptions: N/A.
     |  
     
   **search(self, data_type_name, search_key=None, search_value=None)**  
   
     |      Purpose: Given data type name, key, and value;
     |               find a list of matching BaseDataType instances.
     |      Input Parameters:
     |          data_type_name - name of data type to use as index.
     |          search_key - field name to use as search criteria.
     |          search_value - value to use as search criteria for specified key.
     |      Return: list of BaseDataType (or subclassed) instances.
     |      Exceptions: N/A.
     |  
   **search_with_params(self, data_type_name, dict_)**  
   
     |      Purpose: Given data type name and dictionary of params
     |               find a list of matching BaseDataType instances.
     |      Input Parameters:
     |          data_type_name - name of data type to use as index.
     |          dict_ - OrderedDict containing parameters to use as
     |                  search criteria.
     |      Return: list of BaseDataType (or subclassed) instances.
     |      Exceptions: N/A.
     |  
     
   **start_watchdog(self, data_type)**
   
     |      Purpose: Given data type name; start a watchdog observer
     |               to monitor for file changes at configured path.
     |      Input Parameters:
     |          data_type_name - data type to use as index.
     |      Return: N/A
     |      Exceptions: N/A.
     |  

   **class GroupData(BaseDataType)**  
   
     |  This class implements the structure and functionality
     |  related to data loaded from group file.
     |  
     |  Method resolution order:
     |      GroupData
     |      BaseDataType
     |      __builtin__.object
     |  
     |  Methods defined here:
     |  
     |  __init__(self)
     |  
     |  load_from_list(self, list_)
     |      Purpose: Load fields from list of values passed in.
     |      Input Parameters: list_, list of values in order saved in group file.
     |      Return: N/A.
     |      Exceptions: N/A.
     |  
    
   **class PasswordData(BaseDataType)**  

     |  This class implements the structure and functionality
     |  related to data loaded from passwd file.
     |  
     |  Method resolution order:
     |      PasswordData
     |      BaseDataType
     |      __builtin__.object
     |  
     |  Methods defined here:
     |  
     |  __init__(self)
     |  
     
   **load_from_list(self, list_)**
   
     |      Purpose: Load fields from list of values passed in.
     |      Input Parameters: list_, list of values in order saved in passwd file.
     |      Return: N/A.
     |      Exceptions: N/A.
     |  
    
   **class PathError(exceptions.RuntimeError)**  
   
     |  This class when raised conveys that an exceptional
     |  situation occurred while trying load the passwd
     |  or group files respectively; i.e. bad path to file.
     |  

    
   **class QueryError(exceptions.RuntimeError)**
   
     |  This class when raised provides conveys that an exceptional
     |  situation occurred while trying to process a query.
     |  


# DATA

   **GRP_TYPENAME** = 'GroupData'  
   **PWD_TYPENAME** = 'PasswordData'  
   **logger** = <logging.Logger object>  
   **settings** = <LazySettings "settings">  


