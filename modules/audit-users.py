#!/usr/bin/env python2
# -.- coding: utf-8 -.-

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
module: audit-users
short_description: Get a list of system users
description:
     - Get a list of system users.
author:
    - "Aleksandr Seleznev (@seleznev)"
'''

import os

def main():
    module = AnsibleModule(
        argument_spec = {}
    )

    users = {}

    if not os.path.exists("/etc/passwd"):
        module.fail_json(msg="/etc/passwd does not exist")

    if not os.path.exists("/etc/shadow") or not os.access("/etc/shadow", os.R_OK):
        module.fail_json(msg="unable to open /etc/shadow")

    for line in open("/etc/passwd").readlines():
        data = line.strip().split(":")

        user_name = data[0]
        user = {
            "uid": data[2],
            "gid": data[3],
            "home": data[5],
            "shell": data[6],
            "can_login": True # default
        }

        if user["shell"] in ("/usr/sbin/nologin", "/sbin/nologin", "/bin/false"):
            user["can_login"] = False

        users[user_name] = user

    for line in open("/etc/shadow").readlines():
        data = line.split(":")

        user_name = data[0]
        password = data[1]

        if not len(password) or password[0] in ("x", "*", "!"):
            users[user_name]["can_login"] = False

    module.exit_json(changed=False, ansible_facts={"audit_users": users})

from ansible.module_utils.basic import *
if __name__ == "__main__":
    main()
