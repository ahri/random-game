import re
import json
from os import startfile
from random import randint
from _winreg import ConnectRegistry, OpenKey, CloseKey, EnumValue, HKEY_LOCAL_MACHINE


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

steam_cfg = r'%s\config\config.vdf' % steam_install_path


config = ''.join(open(steam_cfg).readlines())
config = config.replace('{', ':{')
config = config.replace('}', '},')
config = re.sub(r'"\t+"', '":"', config)
config = re.sub(r'":".*"', r'\g<0>,', config, flags=re.MULTILINE)
config = re.sub(r',[\t\n]*\}', '}', config)
config = "{%s" % config
config = re.sub(r',\n$', '}', config)
config = json.loads(config)


apps = config['InstallConfigStore']['Software']['Valve']['Steam']['apps']


installed_apps = []
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

    installed_apps.append(app)

selected = installed_apps[randint(0, len(installed_apps)-1)]
print "Running:", selected
startfile('steam://store/%s' % selected)
