#!/usr/bin/env python2
# -.- coding: utf-8 -.-

# audit-software module based on ideas from hostname module for Ansible
# (ansible-modules-core/system/hostname.py) created by Hiroaki Nakamura
#
# (c) 2016, Aleksandr Seleznev <alex.n.seleznev@gmail.com>
# (c) 2013, Hiroaki Nakamura <hnakamur@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION = '''
---
module: audit-software
short_description: Get a list of installed software
description:
     - Get a list of installed software.
author:
    - "Aleksandr Seleznev (@seleznev)"
    - "Hiroaki Nakamura (@hnakamur)"
    - "Hideki Saito (@saito-hideki)"
'''

class UnimplementedStrategy(object):
    def __init__(self, module):
        self.module = module

    def get_software(self):
        self.unimplemented_error()

    def get_packages(self):
        self.unimplemented_error()

    def unimplemented_error(self):
        platform = get_platform()
        distribution = get_distribution()
        if distribution is not None:
            msg_platform = "%s (%s)" % (platform, distribution)
        else:
            msg_platform = platform
        self.module.fail_json(
            msg="audit-software module cannot be used on platform %s" % msg_platform)

class Software(object):
    platform = "Generic"
    distribution = None
    strategy_class = UnimplementedStrategy

    def __new__(cls, *args, **kwargs):
        return load_platform_subclass(Software, args, kwargs)

    def __init__(self, module):
        self.module = module
        self.strategy = self.strategy_class(module)

    def get_software(self):
        return self.strategy.get_software()

class GenericStrategy(object):

    KNOWN_SOFTWARE = {}

    def __init__(self, module):
        self.module = module

    def get_software(self):
        software = {}
        packages = self.get_packages()

        for name, pkg_name in self.KNOWN_SOFTWARE.items():
            if type(pkg_name) == str:
                if not pkg_name in packages:
                    continue
            elif type(pkg_name) == list:
                pkg_list = filter(lambda x: x in packages, pkg_name)
                if len(pkg_list) > 0:
                    pkg_name = pkg_list[0]
                else:
                    continue
            else:
                module.fail_json(msg="wrong package list type for %s" % name)

            # only if found package
            software[name] = {
                "version": packages[pkg_name]["version"]
            }

        return software

    def get_packages(self):
        return {}

    def get_apache2_modules(self, cmd="apachectl"):
        (rc, out, err) = self.module.run_command("%s -t -D DUMP_MODULES" % cmd, check_rc=True)

        modules = []
        for line in out.splitlines():
            if not line.startswith(" "):
                continue
            module_name = line.strip().split()[0]

            if module_name.endswith("_module"):
                module_name = module_name[:-7]

            modules.append(module_name)

        return modules

    def get_php_modules(self, cmd="php"):
        (rc, out, err) = self.module.run_command("%s -m" % cmd, check_rc=True)

        modules = []
        for line in out.splitlines():
            line = line.strip()
            if len(line) and not line.startswith("["):
                if not line in modules:
                    modules.append(line)

        return modules

    def get_zabbix_servers(self, conf_path="/etc/zabbix/zabbix_agentd.conf"):
        zabbix_servers = None
        try:
            with open(conf_path, "rb") as f:
                for line in f.readlines():
                    if not line.startswith("Server"):
                        continue
                    zabbix_servers = line.split("=")[1].strip().split(",")
        except Exception, err:
            self.module.fail_json(msg="failed to read \"%s\": %s" % (conf_path, str(err)))

        return zabbix_servers

# ===========================================

class DebianStrategy(GenericStrategy):

    KNOWN_SOFTWARE = {
        "Apache2": ["apache2", "apache2-mpm-prefork"],
        "Exim4": ["exim4-daemon-light", "exim4-daemon-heavy"],
        "Git": "git",
        "Lsyncd": "lsyncd",
        "MariaDB (server)": "mariadb-server",
        "Mercurial": "mercurial",
        "Minetest (server)": "minetest-server",
        "MySQL (server)": "mysql-server",
        "Nginx": "nginx",
        "OpenSSH (server)": "openssh-server",
        "PHP": ["php5", "php7.0"],
        "PHP (fpm)": ["php5-fpm", "php7.0-fpm"],
        "Python 2": "python",
        "Python 3": "python3",
        "Redis (server)": "redis-server",
        "Rsyslog": "rsyslog",
        "Ruby": "ruby",
        "SQLite": "sqlite3",
        "Supervisor": "supervisor",
        "Zabbix (agent)": "zabbix-agent",
    }

    def get_software(self):
        software = GenericStrategy.get_software(self)

        if "Apache2" in software:
            software["Apache2"]["modules"] = self.get_apache2_modules()

        if "PHP" in software:
            software["PHP"]["modules"] = self.get_php_modules()

        if "Zabbix (agent)" in software:
            software["Zabbix (agent)"]["servers"] = self.get_zabbix_servers()

        return software

    def get_packages(self):
        packages = {}

        (rc, out, err) = self.module.run_command("dpkg -l", check_rc=True)
        for line in out.splitlines():
            if not line.startswith("ii"):
                continue
            data = line.strip().split()
            name = data[1]
            packages[name] = {
                "name": name,
                "version": data[2],
                "architecture": data[3],
                "description": data[4]
            }

        return packages

# ===========================================

class RedHatStrategy(GenericStrategy):

    KNOWN_SOFTWARE = {
        "Ansible": "ansible",
        "Apache2": "httpd",
        "ClamAV": "clamav",
        "Csync2": "csync2",
        "Memcached": "memcached",
        "Mercurial": "mercurial",
        "Munin": "munin",
        "MySQL (server)": "mysql-server",
        "Nagios": "nagios-common",
        "nginx": "nginx",
        "ntpd": "ntp",
        "OpenSSH (server)": "openssh-server",
        "Perl": "perl",
        "PHP": "php",
        "Postfix": "postfix",
        "Python 2": "python",
        "Rsyslog": "rsyslog",
        "Samba (client)": "samba-client",
        "Sphinx": "sphinx",
        "SQLite": "sqlite",
        "SQLite2": "sqlite2",
        "Subversion": "subversion",
        "vsftpd": "vsftpd",
        "xinetd": "xinetd",
        "Zabbix (agent)": "zabbix-agent"
    }

    def get_software(self):
        software = GenericStrategy.get_software(self)

        if "Apache2" in software:
            software["Apache2"]["modules"] = self.get_apache2_modules()

        if "PHP" in software:
            software["PHP"]["modules"] = self.get_php_modules()

        return software

    def get_packages(self):
        packages = {}

        rpm_cmd = "rpm -qa --qf '%{name}\t%{version}\t%{arch}\t%{summary}\n'"
        (rc, out, err) = self.module.run_command(rpm_cmd, check_rc=True)
        for line in out.splitlines():
            data = line.strip().split()
            name = data[0]
            packages[name] = {
                "name": name,
                "version": data[1],
                "architecture": data[2],
                "description": data[3]
            }

        return packages

# ===========================================

class CentOSSoftware(Software):
    platform = "Linux"
    distribution = "Centos"
    strategy_class = RedHatStrategy

class DebianSoftware(Software):
    platform = "Linux"
    distribution = "Debian"
    strategy_class = DebianStrategy

# ===========================================

def main():
    module = AnsibleModule(
        argument_spec = {}
    )

    software = Software(module)

    module.exit_json(changed=False,
                     ansible_facts={"audit_software": software.get_software()})

from ansible.module_utils.basic import *
if __name__ == "__main__":
    main()
