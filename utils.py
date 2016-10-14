import re
import sys
reload(sys)  
sys.setdefaultencoding('utf8')
import random
import string


#***************************************************************************************
# Python Header 
# Name:
#		replacer
# Purpose:
#		Replace multiple string elements.
# Call it like this:
# def multiple_replace(string, *key_values):
#    return replacer(*key_values)(string)
# Author:
#		stereodruid(J.G.)
# History:
#		0 - init 
def replacer(*key_values):
    replace_dict = uni(dict(key_values))
    replacement_function = lambda match: replace_dict[match.group(0)]
    pattern = re.compile("|".join([re.escape(k) for k, v in key_values]), re.M)
    return lambda string: pattern.sub(replacement_function, string)
#***************************************************************************************
# Python Header 
#		multiple_replace
# Purpose:
#		caller for replacer
# Author:
#		stereodruid(J.G.)
# History:
#		0 - init 
def multiple_replace(string, *key_values):
    return replacer(*key_values)(string)

#***************************************************************************************
# Python Header 
#        multiple_reSub
# Purpose:
#        reSub all strings insite a dict. Valuse in dict:
# dictReplacements = {'search1' : 'replace with1', 'search2' : 'replace with2'} 
# Author:
#        stereodruid(J.G.)
# History:
#        0 - init 
def multiple_reSub(text, dic):
    for i, j in dic.iteritems():
        text = re.sub(i, j, text)
    return text

def ascii(string):
    if isinstance(string, basestring):
        if isinstance(string, unicode):
           string = string.encode('ascii', 'ignore')
    return string

def uni(string):
    if isinstance(string, basestring):
        if isinstance(string, unicode):
           string = string.encode('utf-8', 'ignore' )
    return string