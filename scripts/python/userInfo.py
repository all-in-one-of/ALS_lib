import os

profile = os.path.expandvars("%userprofile%").split('\\')[-1]
users = {'a.grabovski' : 'a.grabovski',
         'a.krylevsky' : 'a.krylevsky',
         'Anton'       : 'a.grabovski',}

user  = users[profile] if profile in users else 'default'