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
module: audit-network
short_description: Get information about network settings
description:
     - Get information about network interfaces, routing tables and
       TCP/UDP sockets.
author:
    - "Aleksandr Seleznev (@seleznev)"
'''

def main():
    module = AnsibleModule({})

    network = {}

    #
    # Interfaces
    #
    (rc, out, err) = module.run_command("ip address show", check_rc=True)

    network["interfaces"] = {}
    for line in out.splitlines():
        r = re.search("^[\d]+:\s([^:]+):.*$", line)
        if r:
            current_interface = r.group(1)
            network["interfaces"][current_interface] = []

        r = re.search("^[\s]+(inet|inet6)\s([a-z0-9:\.]+)\/.*$", line)
        if r:
            ip_address = r.group(2)
            network["interfaces"][current_interface].append(ip_address)

    #
    # Routing tables
    #

    (rc, out, err) = module.run_command("ip route show", check_rc=True)
    network["routes"] = out.strip("\n")

    #
    # TCP/UDP sockets
    #

    network["sockets"] = []
    (rc, out, err) = module.run_command("ss -altupn", check_rc=True)
    for line in out.splitlines():
        if not line.startswith("tcp") and not line.startswith("udp"):
            continue
        data = line.strip().split()
        netid = data[0]
        state = data[1].lower()
        (address, port) = data[4].rsplit(":", 1)
        process = data[6][8:-2].split("),(")[0].split("\"")[1] # users:(("name",pid=000,fd=000),<...>)

        network["sockets"].append({
            "type": netid,
            "state": state,
            "address": address,
            "port": port,
            "process": process
        })

    module.exit_json(changed=False, ansible_facts={"audit_network": network})

from ansible.module_utils.basic import *
if __name__ == "__main__":
    main()
