#!/usr/bin/env python2
# -.- coding: utf-8 -.-

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
import subprocess

def main():
    module = AnsibleModule(
        argument_spec = {}
    )
    facts = {}

    cmd = ["uname", "-a"]
    try:
        facts["uname"] = subprocess.check_output(cmd, stderr=subprocess.STDOUT,
                                                 universal_newlines=True)
    except Exception, e:
        module.fail_json(msg="unable to launch uname. Exception message: {}".format(e))

    module.exit_json(changed=False, ansible_facts=facts)

from ansible.module_utils.basic import *
if __name__ == "__main__":
    main()
