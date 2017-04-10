from _winreg import *
import os, sys

def remove_duplicates(input_str):
    split_str = input_str.split (";")
    new_split_str = list("")
    new_split_str_low = list("")
    for current_str in split_str:
        if current_str.lower() not in new_split_str_low:
            new_split_str_low.append(current_str.lower())
            new_split_str.append(current_str)
    sep = ";"
    result = sep.join(new_split_str)
    if result.startswith(";"):
        result = result.replace(";", " ", 1)
        result = result.strip()
    return result

def append_env(env_name, append_env_value):
    """Function for append environment variable and remove duplicates"""
    env_obj = CreateKey(HKEY_LOCAL_MACHINE, 'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment')
    print "Adding new value"
    env_value = ""
    try:
        env_value = str(QueryValueEx(env_obj, env_name)[0])
    except (WindowsError):  
        print "No variable with given name was found. New one will be created"
        try:
            print "Variable name = " + env_name
            print "Variable value = " + append_env_value
            env_value = append_env_value
            env_value = remove_duplicates(env_value)
            SetValueEx(env_obj, env_name, 0, REG_EXPAND_SZ, env_value)
        except (WindowsError):          
            CloseKey(env_obj)
            print "Acces is denied"
        CloseKey(env_obj)
        return
    try:
        print "Variable name = " + env_name
        print "Variable append value = " + append_env_value
        env_value += ";" + append_env_value
        env_value = remove_duplicates(env_value)
        SetValueEx(env_obj, env_name, 0, REG_EXPAND_SZ, env_value)
    except (WindowsError):          
        CloseKey(env_obj)
        print "Acces is denied"
    CloseKey(env_obj)

if __name__ == '__main__':
    try:
        env_name = sys.argv[1]
    except (IndexError, ValueError):
        print "No environment variable name specified"
        env_name = None
        env_name = 'PATH'
    try:
        append_env_value = sys.argv[2]
    except (IndexError, ValueError):
        print "No environment variable value specified"
        append_env_value = None
        append_env_value = r'D:\HoudiniProject\ALS_LIB\scripts'

    if env_name != None and append_env_value != None:
        append_env(env_name, append_env_value)