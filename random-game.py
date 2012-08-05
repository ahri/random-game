import re
import json
import os
import sys
from random import randint
from _winreg import ConnectRegistry, OpenKey, CloseKey, EnumValue, HKEY_LOCAL_MACHINE


class UserSpecified(object):

    @classmethod
    def config(cls):
        return r"%s\game_exes.txt" % os.environ['USERPROFILE']

    @classmethod
    def exes(cls):
        files = []
        try:
            for line in open(cls.config(), 'r'):
                line = line.strip()
                try:
                    if line[0] != '#' and line not in files:
                        files.append(line)
                except IndexError:
                    pass # empty line
        except IOError:
            pass

        return files


class Steam(object):

    @classmethod
    def _config_file(cls):
        reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
        steam_reg = OpenKey(reg, r"Software\Valve\Steam")
        steam_install_path = None
        i = 0
        while True:
            k, v, _ = EnumValue(steam_reg, i)
            
            if k == 'InstallPath':
                steam_install_path = v
                break

            i += 1

        return r'%s\config\config.vdf' % steam_install_path

    @classmethod
    def config(cls):
        config = open(cls._config_file(), 'r').read()
        config = config.replace('{', ':{')
        config = config.replace('}', '},')
        config = re.sub(r'"\t+"', '":"', config)
        config = re.sub(r'":".*"', r'\g<0>,', config, flags=re.MULTILINE)
        config = re.sub(r',[\t\n]*\}', '}', config)
        config = "{%s" % config
        config = re.sub(r',\n$', '}', config)
        config = json.loads(config)
        return config

    @classmethod
    def apps(cls):
        try:
            return cls.config()['InstallConfigStore']['Software']['Valve']['Steam']['apps']
        except WindowsError:
            return []


    @classmethod
    def installed_apps(cls):
        apps = cls.apps()
        installed = []
        for app in apps:
            # not interested in uninstalled apps
            if apps[app].get('HasAllLocalContent', "0") != "1":
                continue

            idir = apps[app].get('InstallDir', None)

            # not interested in apps that have no installed dir
            if idir is None:
                continue

            # not interested in test apps
            if 'valvetestapp' in idir:
                continue

            # stuff in user dirs is usually dlc, expansions, etc.
            if '\\common\\' not in idir:
                continue

            installed.append(app)

        return installed


games = UserSpecified.exes()
games.extend(Steam.installed_apps())

if len(games) == 0:
    print "ERROR: No games found: install Steam or add exes to %s" % UserSpecified.config()
    sys.exit(1)

selected = games[randint(0, len(games)-1)]

if re.match("^[0-9]+$", selected):
    print "Displaying Steam game %s" % selected
    os.startfile('steam://store/%s' % selected)
else:
    try:
        os.chdir(os.path.dirname(selected))
        os.startfile(os.path.basename(selected))
    except WindowsError:
        print "ERROR: Could not execute '%s'" % selected
