import re
import json
import os
import sys
from random import randint
from winreg import ConnectRegistry, OpenKey, CloseKey, EnumValue, HKEY_CURRENT_USER


class History(object):

    reset_string = '----- RESET -----'

    @classmethod
    def config(cls):
        return r"%s\game_history.txt" % os.environ['USERPROFILE']

    @classmethod
    def record(cls, game):
        open(cls.config(), 'a').write("%s\n" % game)

    @classmethod
    def recent(cls):
        games = []
        try:
            for game in open(cls.config(), 'r').readlines():
                game = game.strip()
                if game == cls.reset_string:
                    games = []
                    continue

                games.append(game)
        except IOError:
            pass

        return games

    @classmethod
    def reset(cls):
        cls.record(cls.reset_string)


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
    def _apps_dir(cls):
        reg = ConnectRegistry(None, HKEY_CURRENT_USER)
        steam_reg = OpenKey(reg, r"Software\Valve\Steam")
        steam_install_path = None
        i = 0
        while True:
            k, v, _ = EnumValue(steam_reg, i)

            if k == 'SteamPath':
                steam_install_path = v
                break

            i += 1

        return r'%s\steamapps' % steam_install_path

    @classmethod
    def installed_apps(cls):
        installed = []
        pattern = re.compile(r'^appmanifest_(\d+)\.acf')
        for filename in os.listdir(cls._apps_dir()):
            m = pattern.match(filename)
            if m is None:
                continue

            installed.append(m[1])

        return installed


games = UserSpecified.exes()
games.extend(Steam.installed_apps())

if len(games) == 0:
    print("ERROR: No games found: install Steam or add exes to %s" % UserSpecified.config())
    sys.exit(1)

history = History.recent()
not_recently_played = list(filter(lambda g: g not in history, games))

if len(not_recently_played) == 0:
    History.reset()
else:
    games = not_recently_played

selected = games[randint(0, len(games)-1)]
History.record(selected)

if re.match("^[0-9]+$", selected):
    print("Displaying Steam game %s" % selected)
    os.startfile('steam://store/%s' % selected)
else:
    try:
        os.chdir(os.path.dirname(selected))
        os.startfile(os.path.basename(selected))
    except WindowsError:
        print("ERROR: Could not execute '%s'" % selected)
