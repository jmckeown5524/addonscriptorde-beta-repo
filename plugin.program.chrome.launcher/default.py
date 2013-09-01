#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import sys
import re
import os
import subprocess
import xbmcplugin
import xbmcgui
import xbmcaddon


addon = xbmcaddon.Addon()
pluginhandle = int(sys.argv[1])
addonID = addon.getAddonInfo('id')
addonPath = addon.getAddonInfo('path')
translation = addon.getLocalizedString
osWin = xbmc.getCondVisibility('system.platform.windows')
osOsx = xbmc.getCondVisibility('system.platform.osx')
osLinux = xbmc.getCondVisibility('system.platform.linux')
useOwnProfile = addon.getSetting("useOwnProfile") == "true"
useCustomPath = addon.getSetting("useCustomPath") == "true"
startScriptBefore = addon.getSetting("startScriptBefore") == "true"
customPath = str(addon.getSetting("customPath"))
scriptPath = str(addon.getSetting("scriptPath"))

userDataFolder = xbmc.translatePath("special://profile/addon_data/"+addonID)
profileFolder = os.path.join(userDataFolder, 'profile')
siteFolder = os.path.join(userDataFolder, 'sites')

if not os.path.isdir(userDataFolder):
    os.mkdir(userDataFolder)
if not os.path.isdir(profileFolder):
    os.mkdir(profileFolder)
if not os.path.isdir(siteFolder):
    os.mkdir(siteFolder)

youtubeUrl = "http://www.youtube.com/leanback"
vimeoUrl = "http://www.vimeo.com/couchmode"


def index():
    files = os.listdir(siteFolder)
    for file in files:
        if file.endswith(".link"):
            fh = open(os.path.join(siteFolder, file), 'r')
            title = ""
            url = ""
            thumb = ""
            stopPlayback = "no"
            for line in fh.readlines():
                entry = line[:line.find("=")]
                content = line[line.find("=")+1:]
                if entry == "title":
                    title = content.strip()
                elif entry == "url":
                    url = content.strip()
                elif entry == "thumb":
                    thumb = content.strip()
                elif entry == "stopPlayback":
                    stopPlayback = content.strip()
            fh.close()
            addSiteDir(title, url, 'showSite', thumb, stopPlayback)
    addDir("[ Vimeo Couchmode ]", vimeoUrl, 'showSite', os.path.join(addonPath, "vimeo.png"), "yes")
    addDir("[ Youtube Leanback ]", youtubeUrl, 'showSite', os.path.join(addonPath, "youtube.png"), "yes")
    addDir("[B]- "+translation(30001)+"[/B]", "", 'addSite', "")
    xbmcplugin.endOfDirectory(pluginhandle)


def addSite(site="", title=""):
    if site:
        content = "title="+title+"\nurl="+site+"\nthumb=DefaultFolder.png\nstopPlayback=no"
        fh = open(os.path.join(siteFolder, title+".link"), 'w')
        fh.write(content)
        fh.close()
    else:
        keyboard = xbmc.Keyboard('', translation(30003))
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText():
            title = keyboard.getText()
            keyboard = xbmc.Keyboard('http://', translation(30004))
            keyboard.doModal()
            if keyboard.isConfirmed() and keyboard.getText():
                url = keyboard.getText()
                keyboard = xbmc.Keyboard('no', translation(30009))
                keyboard.doModal()
                if keyboard.isConfirmed() and keyboard.getText():
                    stopPlayback = keyboard.getText()
                    content = "title="+title+"\nurl="+url+"\nthumb=DefaultFolder.png\nstopPlayback="+stopPlayback
                    fh = open(os.path.join(siteFolder, title+".link"), 'w')
                    fh.write(content)
                    fh.close()
    xbmc.executebuiltin("Container.Refresh")


def getFullPath(path, url):
    profile = ""
    if useOwnProfile:
        profile = ' --user-data-dir="'+profileFolder+'"'
    return '"'+path+'"'+profile+' --start-maximized --disable-translate --disable-new-tab-first-run --no-default-browser-check --no-first-run --kiosk "'+url+'"'


def showSite(url, stopPlayback):
    if stopPlayback == "yes":
        xbmc.Player().stop()
    if osWin:
        if startScriptBefore and scriptPath:
            subprocess.Popen(scriptPath, shell=False)
        path = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
        path64 = 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe'
        if useCustomPath and os.path.exists(customPath):
            fullUrl = getFullPath(customPath, url)
            subprocess.Popen(fullUrl, shell=False)
        elif os.path.exists(path):
            fullUrl = getFullPath(path, url)
            subprocess.Popen(fullUrl, shell=False)
        elif os.path.exists(path64):
            fullUrl = getFullPath(path64, url)
            subprocess.Popen(fullUrl, shell=False)
        else:
            xbmc.executebuiltin('XBMC.Notification(Info:,'+str(translation(30005))+'!,5000)')
            addon.openSettings()
    elif osOsx:
        if startScriptBefore and scriptPath:
            subprocess.Popen(scriptPath, shell=True)
        path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if useCustomPath and os.path.exists(customPath):
            fullUrl = getFullPath(customPath, url)
            subprocess.Popen(fullUrl, shell=True)
        elif os.path.exists(path):
            fullUrl = getFullPath(path, url)
            subprocess.Popen(fullUrl, shell=True)
        else:
            xbmc.executebuiltin('XBMC.Notification(Info:,'+str(translation(30005))+'!,5000)')
            addon.openSettings()
    elif osLinux:
        if startScriptBefore and scriptPath:
            subprocess.Popen(scriptPath, shell=True)
        path = "/usr/bin/google-chrome"
        if useCustomPath and os.path.exists(customPath):
            fullUrl = getFullPath(customPath, url)
            subprocess.Popen(fullUrl, shell=True)
        elif os.path.exists(path):
            fullUrl = getFullPath(path, url)
            subprocess.Popen(fullUrl, shell=True)
        else:
            xbmc.executebuiltin('XBMC.Notification(Info:,'+str(translation(30005))+'!,5000)')
            addon.openSettings()


def removeSite(title):
    os.remove(os.path.join(siteFolder, title+".link"))
    xbmc.executebuiltin("Container.Refresh")


def editSite(title):
    file = os.path.join(siteFolder, title+".link")
    fh = open(file, 'r')
    title = ""
    url = ""
    thumb = "DefaultFolder.png"
    stopPlayback = "no"
    for line in fh.readlines():
        entry = line[:line.find("=")]
        content = line[line.find("=")+1:]
        if entry == "title":
            title = content.strip()
        elif entry == "url":
            url = content.strip()
        elif entry == "thumb":
            thumb = content.strip()
        elif entry == "stopPlayback":
            stopPlayback = content.strip()
    fh.close()

    oldTitle = title
    keyboard = xbmc.Keyboard(title, translation(30003))
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        title = keyboard.getText()
        keyboard = xbmc.Keyboard(url, translation(30004))
        keyboard.doModal()
        if keyboard.isConfirmed() and keyboard.getText():
            url = keyboard.getText()
            keyboard = xbmc.Keyboard(stopPlayback, translation(30009))
            keyboard.doModal()
            if keyboard.isConfirmed() and keyboard.getText():
                stopPlayback = keyboard.getText()
                content = "title="+title+"\nurl="+url+"\nthumb="+thumb+"\nstopPlayback="+stopPlayback
                fh = open(os.path.join(siteFolder, title+".link"), 'w')
                fh.write(content)
                fh.close()
                if title != oldTitle:
                    os.remove(os.path.join(siteFolder, oldTitle+".link"))
    xbmc.executebuiltin("Container.Refresh")


def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


def addDir(name, url, mode, iconimage, stopPlayback=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+urllib.quote_plus(mode)+"&stopPlayback="+urllib.quote_plus(stopPlayback)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addSiteDir(name, url, mode, iconimage, stopPlayback):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+urllib.quote_plus(mode)+"&stopPlayback="+urllib.quote_plus(stopPlayback)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.addContextMenuItems([(translation(30006), 'RunPlugin(plugin://'+addonID+'/?mode=editSite&url='+urllib.quote_plus(name)+')',), (translation(30002), 'RunPlugin(plugin://'+addonID+'/?mode=removeSite&url='+urllib.quote_plus(name)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
name = urllib.unquote_plus(params.get('name', ''))
url = urllib.unquote_plus(params.get('url', ''))
stopPlayback = urllib.unquote_plus(params.get('stopPlayback', 'no'))


if mode == 'addSite':
    addSite()
elif mode == 'showSite':
    showSite(url, stopPlayback)
elif mode == 'removeSite':
    removeSite(url)
elif mode == 'editSite':
    editSite(url)
else:
    index()
