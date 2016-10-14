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
import urllib, urllib2
import time, datetime
import os, sys, re, traceback
import xbmcplugin, xbmcgui, xbmcaddon, xbmcvfs
from utils import *

#todo save user strm pref. to settings

def requestItem(file, fletype='video'):
    log("requestItem") 
    json_query = ('{"jsonrpc":"2.0","method":"Player.GetItem","params":{"playerid":1,"properties":["thumbnail","fanart","title","year","mpaa","imdbnumber","description","season","episode","playcount","genre","duration","runtime","showtitle","album","artist","plot","plotoutline","tagline","tvshowid"]}, "id": 1}')
    json_folder_detail = sendJSON(json_query)
    return re.compile( "{(.*?)}", re.DOTALL ).findall(json_folder_detail)
          
def requestList(path, fletype='video'):
    log("requestList, path = " + path) 
    json_query = ('{"jsonrpc": "2.0", "method": "Files.GetDirectory", "params": {"directory": "%s", "media": "%s", "properties":["thumbnail","fanart","title","year","mpaa","imdbnumber","description","season","episode","playcount","genre","duration","runtime","showtitle","album","artist","plot","plotoutline","tagline","tvshowid"]}, "id": 1}'%(path,fletype))
    json_folder_detail = sendJSON(json_query)
    return re.compile( "{(.*?)}", re.DOTALL ).findall(json_folder_detail)      
   
def fillPluginItems(url, wSTRM=False):
    log('fillPluginItems')
    #todo media_type by plugin path, ie. plugin.video, plugin.music
    media_type='video'
    
    #todo needed var?
    file_type=False
    strm=False
    strm_name=''
    strm_type='Other'
    #
    
    if not file_type:
        detail = uni(requestList(url, media_type))
    else:
        detail = uni(requestItem(url, media_type))
        
    for f in detail:
        files = re.search('"file" *: *"(.*?)",', f)
        filetypes = re.search('"filetype" *: *"(.*?)",', f)
        labels = re.search('"label" *: *"(.*?)",', f)
        thumbnails = re.search('"thumbnail" *: *"(.*?)",', f)
        fanarts = re.search('"fanart" *: *"(.*?)",', f)
        descriptions = re.search('"description" *: *"(.*?)",', f)
        
        if filetypes and labels and files:
            filetype = filetypes.group(1)
            label = cleanLabels(labels.group(1))
            file = (files.group(1).replace("\\\\", "\\"))
            
            if not descriptions:
                description = ''
            else:
                description = cleanLabels(descriptions.group(1))
                
            thumbnail = removeNonAscii(thumbnails.group(1))
            fan = removeNonAscii(fanarts.group(1))
            
            #todo parse json for infolabels to pass to kodi player on playback & to write file nfos.
            infoList = False
            infoArt = False
            
            # todo disabled while debugging.
            # if REAL_SETTINGS.getSetting('Link_Type') == '0':
                # link=sys.argv[0]+"?url="+urllib.quote_plus(file)+"&mode="+str(10)+"&name="+urllib.quote_plus(label)+"&infoList="+urllib.quote_plus(str(infoList))+"&infoArt="+urllib.quote_plus(str(infoArt))
            # else:
            link = file
            
        
            # if strm_type in ['TV','Episodes']:
                # path = os.path.join('TV',strm_name)
                # filename = strm_name + ' - ' + label
                # print path, filename
                            
            # if strm_type in ['TV']:
                # path = os.path.join('TV',strm_name)
                # filename = strm_name + ' - ' + label
                # print path, utils.multiple_reSub(filename.rstrip(), dictReplacements)
                
            # if strm_type in ['Cinema']:
                # path = os.path.join('Cinema',strm_name)
                # filename =   utils.multiple_reSub(label.rstrip(), dictReplacements)
                # print path, filename
                
            # if strm_type in ['TV-Shows']:
                # if showtitle and season and episode:
# #                     if showtitle == "":
# #                         showtitle = strm_name
                    # path = os.path.join('TV-Shows',showtitle)    
                    # filename = 's' + season + 'e' + episode
                    # print path, filename  
                # else:
                    # path = os.path.join('Other', strm_name)
                    # filename = strm_name + ' - ' + label
                    # print path, filename    
                
                #todo regex for info from label if no meta is returned from json
                # if strm_type in ['TV','Episodes']:
                # if url.find('??/')==0:
                # episode = re.search('"episode":(.?),', f).group(1) 
                # season = re.search('"season":(.?),', f).group(1) 
                # title = urllib.quote(re.search('"showtitle" : *"(.?)",', f).group(1).strip()).replace('/','-').replace('\','-')
                # episode_title = urllib.quote(re.search('"title" : *"(.?)",', f).group(1).strip()).replace('/','-').replace('\','-')
                # path = os.path.join('TV',title,'Season '+season)
                # filename = 'S'+season+'E'+episode+' '+episode_title
                # else:
                    # path = os.path.join('TV',strm_name)
                    # filename = strm_name + ' - ' + label
                    # print path, filename
# ..
                
            if filetype == 'file':
                if wSTRM:
                    writeSTRM(cleanStrms(file), cleanStrms(filename) ,link)
                else:
                    addLink(label,link,infoList,infoArt,len(detail))
            else:
                if wSTRM:
                    fillPluginItems(file)
                else:
                    addDir(label,link,2,infoList,infoArt)
        
def fillPlugins(type='video'):
    log('fillPlugins, type = ' + type)
    json_query = ('{"jsonrpc":"2.0","method":"Addons.GetAddons","params":{"type":"xbmc.addon.%s","properties":["name","path","thumbnail","description","fanart","summary"]}, "id": 1 }'%type)
    json_detail = sendJSON(json_query)
    detail = re.compile( "{(.*?)}", re.DOTALL ).findall(json_detail)
    for f in detail:
        names = re.search('"name" *: *"(.*?)",', f)
        paths = re.search('"addonid" *: *"(.*?)",', f)
        thumbnails = re.search('"thumbnail" *: *"(.*?)",', f)
        fanarts = re.search('"fanart" *: *"(.*?)",', f)
        descriptions = re.search('"description" *: *"(.*?)",', f)
        if not descriptions:
            descriptions = re.search('"summary" *: *"(.*?)",', f)
        if descriptions:
            description = cleanLabels(descriptions.group(1))
        else:
            description = ''
            
        #todo parse json for infolabels to pass to kodi player on playback & to write file nfos.
        infoList = False
        infoArt = False
        if names and paths:
            name = cleanLabels(names.group(1))
            path = paths.group(1)
            if type == 'video' and path.startswith('plugin.video') and not path.startswith('plugin.video.pseudo.companion'):
                thumbnail = removeNonAscii(thumbnails.group(1))
                fan = removeNonAscii(fanarts.group(1))
                addDir(name,'plugin://'+path,2,infoList,infoArt)
                
def getSources():
    log('getSources')
    addDir('Video Plugins','video',1)
    addDir('Music Plugins','music',1)
    addDir('UPNP Servers','upnp://',2)
    addDir('PVR Backend','pvr://',2)

def makeSTRM(filepath, filename, url):
    log('makeSTRM')
    filepath = os.path.join(STRM_LOC, filepath)
    if not xbmcvfs.exists(filepath): 
        xbmcvfs.mkdirs(filepath)
    fullpath = os.path.join(filepath, filename + '.strm')
    if REAL_SETTINGS.getSetting('Clear_Strms') == 'true':
        try: 
            xbmcvfs.delete(fullpath)
        except:
            pass
    fle = open(fullpath, "w")
    fle.write("%s" % url)
    fle.close()
        
def writeSTRM(path, file, url):
    log('writeSTRM')
    #todo proper write up, code should generate paths with optional bindings to the plugin.
    if url.find("plugin://plugin.video.pseudo.library/?url=plugin") == -1:
        url = url.strip().replace("?url=plugin", "plugin://plugin.video.pseudo.library/?url=plugin", 1)
    makeSTRM(path, file, url)
          
def getType():
    Types = ['TVShow','Episode','Movies','Other']
    select = selectDialog(Types)
    if select >= 0:
        return Types[select]

# Adapted from Ronie's screensaver.picture.slideshow * https://github.com/XBMC-Addons/screensaver.picture.slideshow/blob/master/resources/lib/utils.py    
def walk(path):     
    log("walk " + path)
    MEDIA_TYPES = ['.avi', '.mp4', '.m4v', '.3gp', '.3g2', '.f4v', '.mov', '.mkv', '.flv', '.ts', '.m2ts', '.mts', '.strm']
    video = []
    folders = []
    # multipath support
    if path.startswith('multipath://'):
        # get all paths from the multipath
        paths = path[12:-1].split('/')
        for item in paths:
            folders.append(urllib.unquote_plus(item))
    else:
        folders.append(path)
    for folder in folders:
        if xbmcvfs.exists(xbmc.translatePath(folder)):
            # get all files and subfolders
            dirs,files = xbmcvfs.listdir(os.path.join(xbmc.translatePath(folder),''))
            # natural sort
            convert = lambda text: int(text) if text.isdigit() else text
            alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
            files.sort(key=alphanum_key)
            for item in files:
                # filter out all video
                if os.path.splitext(item)[1].lower() in MEDIA_TYPES:
                    video.append([os.path.join(folder,item), ''])
            for item in dirs:
                # recursively scan all subfolders
                video += self.walk(os.path.join(folder,item,'')) # make sure paths end with a slash
    # cleanup   
    del folders[:]
    return video
    
def getVideo(url, infoList, infoArt):
    #todo build player listitem
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, xbmcgui.ListItem(path=url))
    
params=get_params()
url=None
name=None
mode=None
infoList=None
infoArt=None

try:
    url=urllib.unquote_plus(params["url"])
except:
        pass
try:
    name=urllib.unquote_plus(params["name"])
except:
        pass
try:
    mode=int(params["mode"])
except:
        pass
try:
    infoList=int(params["infoList"])
except:
        pass
try:
    infoArt=int(params["infoArt"])
except:
        pass
        
log("Mode: "+str(mode))
log("URL:  "+str(url))
log("Name: "+str(name))
log("infoList: "+str(infoList))
log("infoArt: "+str(infoArt))

if mode == None: getSources()
elif mode == 1: fillPlugins(url)
elif mode == 2: fillPluginItems(url)

#todo expand sort support
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL )
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE )
xbmcplugin.endOfDirectory(int(sys.argv[1]),cacheToDisc=False) # End List

#todo create strm contextMenu, set config to file, service to parse set config and recreate strms
