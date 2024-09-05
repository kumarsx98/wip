import xmlsec
print(xmlsec.__file__)
import os
print(os.path.dirname(xmlsec.__file__))
print(os.path.join(os.path.dirname(xmlsec.__file__), 'xmlsec1.exe'))