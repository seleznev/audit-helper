# audit-helper

Simple script that can help to get basic info about GNU/Linux host.

```
$ audit-helper --template=example.j2 user@hostname
```

Script get list of Ansible modules (in `modules` directory), prepare and run
Ansible playbook via [Python API](http://docs.ansible.com/ansible/dev_guide/developing_api.html).
Then it collects `ansible_facts` from every module and use Jinja2 to convert
template into report (prints to stdout).

---

One of most usefull key is `--ask-pass` (works like in Ansible):


```
$ audit-helper --help
usage: audit-helper [-h] [--version] [-v] [--exclude-module EXCLUDE_MODULE]
                    [-t TEMPLATE] [-k]
                    user@hostname

positional arguments:
  user@hostname         user (optional) and host to connect

optional arguments:
  -h, --help            show this help message and exit
  --version             print program version
  -v, --verbose         increase output verbosity
  --exclude-module EXCLUDE_MODULE
                        exclude module by name
  -t TEMPLATE, --template TEMPLATE
                        path to report template (default: report.j2)
  -k, --ask-pass        ask for connection passwords
```
