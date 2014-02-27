#!/usr/bin/env python
"""
Gets node dependencies from gxpc stat
"""


import sys
import subprocess
import json

def depth(line):
    n=0
    for char in line:
        if char == ' ':
            n += 1
        else:
            return n
    return n

def name(line):
    return line.split('-')[0].strip()
        
def depth_name(line):
    n=0
    for char in line:
        if char == ' ':
            n += 1
        else:
            break
    return  line.split('-')[0].strip(), n
    
def childs(node, node_list):
    childs = list()
    for i in range(len(node_list)):
        if node == node_list[i][0]:
            for j in range(i+1, len(node_list)):
                if node_list[j][1] == node_list[i][1] + 1:
                    childs.append(node_list[j][0])
                if node_list[j][1] <= node_list[i][1]:
                    return childs
    return childs

def tree():
    deps = {}
    node_list = list()

    lines = subprocess.Popen(['gxpc', 'stat'], stdout=subprocess.PIPE).communicate()[0].split('\n')
    lines = lines[1:-1]

    for line in lines:
        node_list.append(depth_name(line))
        deps[node_list[-1][0]] = [[]]

    for node in deps.keys():
        deps[node][0] = childs(node, node_list)

    return deps

def save_dep(dep, filename):
    f = open(filename, 'w')
    f.write(json.dumps(dep))
    f.close()

def read_dep(filename):
    f_dep = open('dep.txt', 'r').read()
    read_deps = json.loads(f_dep)
    deps = {}
    for key, val in read_deps.items():
        key = key.encode('ascii', 'replace')

        for i in range(len(val)):
            for j in range(len(val[i])):
                val[i][j] = val[i][j].encode('ascii', 'replace')

        deps[key] = val
            
    return deps

def main():
    deps = tree()
    print deps
    save_dep(deps, 'dep.txt')
    read_d = read_dep('dep.txt')
    print "Read dependency:"
    print read_d
    
    
if __name__ == '__main__':
    sys.exit(main())


