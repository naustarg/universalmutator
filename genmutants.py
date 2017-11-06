import sys
import shutil
import mutator

import python_handler
import python3_handler
import c_handler
import java_handler
import swift_handler

try:
    import custom_handler
except:
    pass

handlers = {"python": python_handler,
            "python3": python3_handler,
            "c": c_handler,
            "java": java_handler,
            "swift": swift_handler}

languages = {".c": "c",
             ".py": "python",
             ".java": "java",
             ".swift": "swift"}    

try:
    handlers["custom"] == "custom_handler"
except:
    pass

sourceFile = sys.argv[1]
ending = "." + sourceFile.split(".")[-1]

if len(sys.argv) < 3:
    language = languages[ending]
    otherRules = []
else:
    language = sys.argv[2]
    otherRules = sys.argv[3:]

base = ".".join((sourceFile.split(".")[:-1]))

if language in ["c","java","swift"]:
    otherRules.append("c_like.rules")

rules = ["universal.rules",language + ".rules"] + otherRules

source = []

with open(sourceFile,'r') as file:
    for l in file:
        source.append(l)
        
mutants = mutator.mutants(source, rules = rules)

print len(mutants),"MUTANTS GENERATED BY RULES"

validMutants = []
invalidMutants = []
redundantMutants = []
uniqueMutants = {}

handler = handlers[language]

mutantNo = 0
for mutant in mutants:
    tmpMutantName = "tmp_mutant" + ending
    print "PROCESSING MUTANT:",str(mutant[0])+":",source[mutant[0]-1][:-1]," ==> ",mutant[1][:-1],"...",
    mutator.makeMutant(source, mutant, tmpMutantName)
    mutantResult = handler.handler(tmpMutantName, mutant, sourceFile, uniqueMutants)
    print mutantResult,
    mutantName = base + ".mutant." + str(mutantNo) + ending
    if mutantResult == "VALID":
        print "[written to",mutantName+"]",
        shutil.copy(tmpMutantName, mutantName)
        validMutants.append(mutant)
        mutantNo += 1
    elif mutantResult == "INVALID":
        invalidMutants.append(mutant)
    elif mutantResult == "REDUNDANT":
        redundantMutants.append(mutant)
    print

print len(validMutants),"VALID MUTANTS"
print len(invalidMutants),"INVALID MUTANTS"
print len(redundantMutants),"REDUNDANT MUTANTS"
            

