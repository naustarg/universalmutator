import sys
import re
import subprocess
import dis
import marshal
import struct
import time
import types
import os
import shutil

input = sys.argv[1]

def getCode(fname):
    # Courtesy of Ned Batchelder, just get the code object from the .pyc file
    f = open(fname, "rb")
    magic = f.read(4)
    moddate = f.read(4)
    # Note that for Python 3.3+ you'd need another f.read(4) here since the format changed
    code = marshal.load(f)
    return code

rulesText = []

with open("mutation.rules",'r') as file:
    for l in file:
        rulesText.append(l)

rules = []
for r in rulesText:
    try:
        s = r.split(" ==> ")
        lhs = re.compile(s[0])
        if (len(s[1]) > 0) and (s[1][-1] == "\n"):
            rhs = s[1][:-1]
        else:
            rhs = s[1]
        rules.append((lhs,rhs))
    except Exception as e:
        print e
        print "FAILED TO COMPILE RULE:",r
        
source = []

with open(input,'r') as file:
    for l in file:
        source.append(l)

mutants = []
lineno = 0
for l in source:
    lineno += 1
    for (lhs,rhs) in rules:
        pos = 0
        p = lhs.search(l,pos)
        while p and (pos < len(l)):
            pos = p.start()+1
            mutant = l[:p.start()] + lhs.sub(rhs,l[p.start():],count=1)
            if mutant[-1] != "\n":
                mutant += "\n"
            mutants.append((lineno,mutant))
            print "NEW MUTANT OF LINE",lineno," = ",
            print "  ",mutant,
            p = lhs.search(l,pos)

print len(mutants),"MUTANTS GENERATED BY RULES"

validMutants = []
invalidCount = 0
redundantCount = 0

uniqueCode = []
if os.path.exists("tmp_mutant.pyc"):
    os.remove("tmp_mutant.pyc")
shutil.copy(input,"tmp_mutant.py")
with open("mutant_output",'w') as file:
    subprocess.call(["python","handlemutant.py"],stdout=file,stderr=file)
assert(os.path.exists("tmp_mutant.pyc"))
uniqueCode.append(getCode("tmp_mutant.pyc"))

mutantNo = 0
for (lmod,mutant) in mutants:
    print "PROCESSING MUTANT",mutant[:-1],"OF LINE",lmod,"...",
    lineno = 0            
    with open("tmp_mutant.py",'w') as file:
        for l in source:
            lineno += 1
            if lineno != lmod:
                file.write(l)
            else:
                file.write(mutant)
    if os.path.exists("tmp_mutant.pyc"):
        os.remove("tmp_mutant.pyc")
    with open("mutant_output",'w') as file:
        subprocess.call(["python","handlemutant.py"],stdout=file,stderr=file)
    if os.path.exists("tmp_mutant.pyc"):
        c = getCode("tmp_mutant.pyc")
        if c in uniqueCode:
            print "REDUNDANT"
            redundantCount += 1
            continue
        validMutants.append((lmod,mutant))
        uniqueCode.append(c)
        shutil.copy("tmp_mutant.py","mutant." + str(mutantNo) + ".py")
        print "VALID!"
        mutantNo += 1
    else:
        print "INVALID"
        invalidCount += 1

print len(validMutants),"VALID MUTANTS"
print "(",invalidCount,"INVALID",redundantCount,"REDUNDANT )"
            
