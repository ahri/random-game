import re
import json
from os import startfile
from random import randint

config = ''.join(open(r'd:\steam\config\config.vdf').readlines())
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

for app in installed_apps:
	print app, apps[app]['InstallDir']

selected = installed_apps[randint(0, len(installed_apps)-1)]
print "Running:", selected
startfile('steam://store/%s' % selected)
