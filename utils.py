#   Copyright (C) 2016 Lunatixz
#
#
# This file is part of PseudoLibrary.
#
# PseudoLibrary is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PseudoLibrary is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PseudoLibrary.  If not, see <http://www.gnu.org/licenses/>.

# -*- coding: utf-8 -*-
import os, re, sys, time, zipfile, requests, random, traceback
import urllib, urllib2,cookielib, base64, fileinput, shutil, socket, httplib, urlparse, HTMLParser
import xbmc, xbmcgui, xbmcplugin, xbmcvfs, xbmcaddon
import time, _strptime, string, datetime, ftplib, hashlib, smtplib, feedparser, imp, operator

from pyfscache import *
from xml.etree import ElementTree as ET
from xml.dom.minidom import parse, parseString
from datetime import timedelta
      
if sys.version_info < (2, 7):
    import simplejson as json
else:
    import json
    
# Plugin Info
ADDON_ID = 'plugin.video.pseudo.library'
REAL_SETTINGS = xbmcaddon.Addon(id=ADDON_ID)
ADDON_ID = REAL_SETTINGS.getAddonInfo('id')
ADDON_NAME = REAL_SETTINGS.getAddonInfo('name')
ADDON_PATH = (REAL_SETTINGS.getAddonInfo('path').decode('utf-8'))
ADDON_VERSION = REAL_SETTINGS.getAddonInfo('version')
SETTINGS_LOC = REAL_SETTINGS.getAddonInfo('profile')
REQUESTS_LOC = xbmc.translatePath(os.path.join(SETTINGS_LOC, 'requests',''))
ICON = os.path.join(ADDON_PATH, 'icon.png')
FANART = os.path.join(ADDON_PATH, 'fanart.jpg')
DEBUG = True#REAL_SETTINGS.getSetting('Enable_Debugging') == 'true'
STRM_LOC = xbmc.translatePath(REAL_SETTINGS.getSetting('STRM_LOC'))
    
# pyfscache globals
from pyfscache import *
cache_daily = FSCache(REQUESTS_LOC, days=1, hours=0, minutes=0)


def log(msg, level = xbmc.LOGDEBUG):
    if DEBUG != True and level == xbmc.LOGDEBUG:
        return
    xbmc.log(ADDON_ID + '-' + ADDON_VERSION + '-' + uni(msg), level)

def cleanString(string):
    newstr = uni(string)
    newstr = newstr.replace('&', '&amp;')
    newstr = newstr.replace('>', '&gt;')
    newstr = newstr.replace('<', '&lt;')
    return uni(newstr)

def uncleanString(string):
    newstr = uni(string)
    newstr = newstr.replace('&amp;', '&')
    newstr = newstr.replace('&gt;', '>')
    newstr = newstr.replace('&lt;', '<')
    return uni(newstr)
    
def replacer(*key_values):
    replace_dict = dict(key_values)
    replacement_function = lambda match: replace_dict[match.group(0)]
    pattern = re.compile("|".join([re.escape(k) for k, v in key_values]), re.M)
    return lambda string: pattern.sub(replacement_function, string)  
    
def multiple_replace(string, *key_values):
    return replacer(*key_values)(string)  

def multiple_reSub(text, dic):
    for i, j in dic.iteritems():
        text = re.sub(i, j, text)
    return text
    
def escapeEncode(string):
    #temp function till I can examine bytestring that is causing problems.
    dictReplacements = {'\xc3\x84' : 'Ae','\xc3\xa4' : 'ae', '\xc3\x96' : 'Oe',
                        '\xc3\xb6' : 'oe','\xc3\x9c' : 'Ue', 'xc3\xbc' : 'ue', 
                        '\xc3\x9f' : 'ss'}
    return multiple_reSub(string.rstrip(), dictReplacements)
       
def cleanLabels(text, format=''):
    log('cleanLabels, IN = ' + text)
    text = escapeEncode(uni(text))
    text = re.sub('\[COLOR (.+?)\]', '', text)
    text = re.sub('\[/COLOR\]', '', text)
    text = re.sub('\[COLOR=(.+?)\]', '', text)
    text = re.sub('\[color (.+?)\]', '', text)
    text = re.sub('\[/color\]', '', text)
    text = re.sub('\[Color=(.+?)\]', '', text)
    text = re.sub('\[/Color\]', '', text)
    text = text.replace("[]",'')
    text = text.replace("[UPPERCASE]",'')
    text = text.replace("[/UPPERCASE]",'')
    text = text.replace("[LOWERCASE]",'')
    text = text.replace("[/LOWERCASE]",'')
    text = text.replace("[B]",'')
    text = text.replace("[/B]",'')
    text = text.replace("[I]",'')
    text = text.replace("[/I]",'')
    text = text.replace('[D]','')
    text = text.replace('[F]','')
    text = text.replace("[CR]",'')
    text = text.replace("[HD]",'')
    text = text.replace("()",'')
    text = text.replace("[CC]",'')
    text = text.replace("[Cc]",'')
    text = text.replace("[Favorite]", "")
    text = text.replace("[DRM]", "")
    text = text.replace('(cc).','')
    text = text.replace('(n)','')
    text = text.replace("(SUB)",'')
    text = text.replace("(DUB)",'')
    text = text.replace('(repeat)','')
    text = text.replace("(English Subtitled)", "")    
    text = text.replace("*", "")
    text = text.replace("\n", "")
    text = text.replace("\r", "")
    text = text.replace("\t", "")
    text = text.replace("/",'')
    text = text.replace("\ ",'')
    text = text.replace("/ ",'')
    text = text.replace("\\",'/')
    text = text.replace("//",'/')
    text = text.replace('/"','')
    text = text.replace('plugin.video.','')
    text = text.replace('plugin.audio.','')

    if format == 'title':
        text = text.title().replace("'S","'s")
    elif format == 'upper':
        text = text.upper()
    elif format == 'lower':
        text = text.lower()
    else:
        text = text
        
    text = uncleanString(text.strip())
    log('cleanLabels, OUT = ' + text)
    return text
    
def cleanStrms( text, format=''):
    text = uni(text)
    text = text.replace('Full Episodes', '')
    if format == 'title':
        text = text.title().replace("'S","'s")
    elif format == 'upper':
        text = text.upper()
    elif format == 'lower':
        text = text.lower()
    else:
        text = text
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

def removeNonAscii(s): return "".join(filter(lambda x: ord(x)<128, s))

def sendJSON(command):
    log('sendJSON')
    data = ''
    try:
        data = xbmc.executeJSONRPC(uni(command))
    except UnicodeEncodeError:
        data = xbmc.executeJSONRPC(ascii(command))
    return uni(data)
      
def addLink(name,url,infoList=False,infoArt=False,total=0,content_type="video",context=False):
    log('addLink')
    liz=xbmcgui.ListItem(name)
    if context:
        contextMenu = []
        contextMenu.append(('Create Strms','XBMC.RunPlugin(%s&mode=200&name=%s)'%(u, name)))
        liz.addContextMenuItems(contextMenu)
    liz.setProperty('IsPlayable', 'true')
    if infoList == False:
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
    else:
        liz.setInfo(type=content_type, infoLabels=infoList)
    if infoArt == False:
        liz.setArt({'thumb': ICON, 'fanart': FANART})
    else:
        liz.setArt(infoArt)
    xbmcplugin.setContent(int(sys.argv[1]), content_type)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz,totalItems=total)
        
def addDir(name,url,mode,infoList=False,infoArt=False,content_type="video",context=False):
    log('addDir')
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    liz=xbmcgui.ListItem(name)
    if context:
        contextMenu = []
        contextMenu.append(('Create Strms','XBMC.RunPlugin(%s&mode=200&name=%s)'%(u, name)))
        liz.addContextMenuItems(contextMenu)
    liz.setProperty('IsPlayable', 'false')
    if infoList == False:
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
    else:
        liz.setInfo(type=content_type, infoLabels=infoList)
    if infoArt == False:
        liz.setArt({'thumb': ICON, 'fanart': FANART})
    else:
        liz.setArt(infoArt)
    xbmcplugin.setContent(int(sys.argv[1]), content_type)
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)

def getProperty(str):
    return xbmcgui.Window(10000).getProperty(str)

def setProperty(str1, str2):
    xbmcgui.Window(10000).setProperty(str1, str2)

def clearProperty(str):
    xbmcgui.Window(10000).clearProperty(str)

def removeStringElem(lst,string=''):
    return ([x for x in lst if x != string])
    
def replaceStringElem(lst,old='',new=''):
    return ([x.replace(old,new) for x in lst])
        
def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
            params=sys.argv[2]
            cleanedparams=params.replace('?','')
            if (params[len(params)-1]=='/'):
                params=params[0:len(params)-2]
            pairsofparams=cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                splitparams={}
                splitparams=pairsofparams[i].split('=')
                if (len(splitparams))==2:
                    param[splitparams[0]]=splitparams[1]             
        return param
            
##################
# GUI Tools #
##################

def handle_wait(time_to_wait,header,title): #*Thanks enen92
    dlg = xbmcgui.DialogProgress()
    dlg.create("PseudoTV Live", header)
    secs=0
    percent=0
    increment = int(100 / time_to_wait)
    cancelled = False
    while secs < time_to_wait:
        secs += 1
        percent = increment*secs
        secs_left = str((time_to_wait - secs))
        remaining_display = "Starts In " + str(secs_left) + " seconds, Cancel Channel Change?" 
        dlg.update(percent,title,remaining_display)
        xbmc.sleep(1000)
        if (dlg.iscanceled()):
            cancelled = True
            break
    if cancelled == True:
        return False
    else:
        dlg.close()
        return True

def show_busy_dialog():
    xbmc.executebuiltin('ActivateWindow(busydialog)')

def hide_busy_dialog():
    xbmc.executebuiltin('Dialog.Close(busydialog)')
    while xbmc.getCondVisibility('Window.IsActive(busydialog)'):
        time.sleep(.1)
        
def Error(header, line1= '', line2= '', line3= ''):
    dlg = xbmcgui.Dialog()
    dlg.ok(header, line1, line2, line3)
    del dlg

def infoDialog(str, header=ADDON_NAME, time=4000):
    try: xbmcgui.Dialog().notification(header, str, THUMB, time, sound=False)
    except: xbmc.executebuiltin("Notification(%s,%s, %s, %s)" % (header, str, time, THUMB))

def okDialog(str1, str2='', header=ADDON_NAME):
    xbmcgui.Dialog().ok(header, str1, str2)

def selectDialog(list, header=ADDON_NAME, autoclose=0):
    if len(list) > 0:
        select = xbmcgui.Dialog().select(header, list, autoclose)
        return select

def yesnoDialog(str1, str2='', header=ADDON_NAME, yes='', no=''):
    answer = xbmcgui.Dialog().yesno(header, str1, str2, '', yes, no)
    return answer
     
def browse(type, heading, shares, mask='', useThumbs=False, treatAsFolder=False, path='', enableMultiple=False):
    retval = xbmcgui.Dialog().browse(type, heading, shares, mask, useThumbs, treatAsFolder, path, enableMultiple)
    return retval
       
def open_url(url, userpass=None):
    log("open_url")
    page = ''
    try:
        request = urllib2.Request(url)
        if userpass:
            user, password = userpass.split(':')
            base64string = base64.encodestring('%s:%s' % (user, password))
            request.add_header("Authorization", "Basic %s" % base64string) 
        else:
            request.add_header('User-Agent','Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')
        page = urllib2.urlopen(request)
        return page
    except urllib2.HTTPError, e:
        return page
        
@cache_daily        
def read_url_cached(url, userpass=False, return_type='read'):
    log("read_url_cached")
    try:
        if return_type == 'readlines':
            response = open_url(url, userpass).readlines()
        else:
            response = open_url(url, userpass).read()
        return response
    except Exception,e:
        pass