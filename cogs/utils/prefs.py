# -*- coding: utf-8 -*-
# !/usr/bin/env python3.5

# TODO: A refaire en se basant sur https://github.com/Rapptz/RoboDanny/blob/32d5b346a66e28f8ff613005b4a819d7154690b2/cogs/utils/config.py
import json
import os

from cogs.utils import commons

cache = True


def getPref(server, pref):
    if not cache or not hasattr(commons, "servers"):
        servers = JSONloadFromDisk("channels.json")
        commons.servers = servers
    else:
        servers = commons.servers
    try:
        return servers[str(server.id)]["settings"].get(pref, commons.defaultSettings[pref]["value"])
    except KeyError:
        return commons.defaultSettings[pref]["value"]


def setPref(server, pref, value=None, force=False):
    if not cache or not hasattr(commons, "servers"):
        servers = JSONloadFromDisk("channels.json")
        commons.servers = servers
    else:
        servers = commons.servers

    if value is not None:

        if not "settings" in servers[server.id]:
            servers[str(server.id)]["settings"] = {}
        try:
            # print(commons.defaultSettings[pref]["type"](value))
            if "min" in commons.defaultSettings[pref].keys():
                if commons.defaultSettings[pref]["type"](value) < commons.defaultSettings[pref]["min"]:
                    return False

            if "max" in commons.defaultSettings[pref].keys():
                if commons.defaultSettings[pref]["type"](value) > commons.defaultSettings[pref]["max"]:
                    return False

            servers[str(server.id)]["settings"][pref] = commons.defaultSettings[pref]["type"](value)

        except ValueError:
            if force:
                servers[str(server.id)]["settings"][pref] = value
            else:
                return False
    else:
        if not "settings" in servers[str(server.id)]:
            return True
        if pref in servers[str(server.id)]["settings"]:
            servers[str(server.id)]["settings"].pop(pref)

    JSONsaveToDisk(servers, "channels.json")
    return True


def JSONsaveToDisk(data, filename):
    with open(filename + ".temp", 'w') as outfile:
        json.dump(data, outfile, sort_keys=True, indent=4)
        # atomically move the file
        os.replace(filename + ".temp", filename)
    if hasattr(commons, "servers"):
        del commons.servers


def JSONloadFromDisk(filename, default="{}", error=False):
    try:
        file = open(filename, 'r')
        data = json.load(file)
        return data
    except IOError:
        if not error:
            file = open(filename, 'w')
            file.write(default)
            file.close()
            return eval(default)
        else:
            raise
