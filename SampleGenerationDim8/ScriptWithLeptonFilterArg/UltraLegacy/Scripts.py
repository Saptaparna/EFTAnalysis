import json
import optparse

usage = 'usage: %prog [options]'
parser = optparse.OptionParser(usage)
parser.add_option('--json', dest='json', help='parameters', default=None, type='string')
(opt, args) = parser.parse_args()

with open(opt.json,"r") as f:
    par = json.load(f)

Path = "Templete"
for sh in par:
    content = ""
    with open("%s/%s"%(Path,sh),"r") as f:
        content = f.read()
    for ireplace in par[sh]:
        content = content.replace(ireplace,par[sh][ireplace])
    with open(sh,"w") as f:
        f.write(content)
