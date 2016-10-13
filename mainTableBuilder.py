from mbnfParser import parseFile
from scanner import getSymbolsToIDs, getIDsToSymbols

SEMICOLON=1
DERIVES=2
ALSODERIVES=3
EPSILON=4
SYMBOL=5
EOF=6

def printFirsts(firsts, IDToSymb):
    for symbol in firsts:
        firstStr = "[ "
        for symbolsFirsts in firsts[symbol]:
            firstStr += IDToSymb[symbolsFirsts] + " , "
        print IDToSymb[symbol] + " : " + firstStr[:-2] + "]"

#TODO: terminals shouldn't have EOF and EPSILON
#TODO: Also making assumption EPSILON = empty
def getFirsts(nonTerminals, terminals, productions, IDToSymb):
    FIRST = {}
    # ACTUAL TODO: might need to add in epsilon and eof
    allSymbs = terminals.union(nonTerminals).union(set([EPSILON, EOF]))

    # TODO: Should be terminals U EOF U epsilon
    for a in terminals.union(set([EOF, EPSILON])):
        FIRST[a] = set([a])
    for A in nonTerminals:
        FIRST[A] = set()

    changing = True
    while changing:
        changing = False
        # A is nonterminal
        for A in productions:
            AsProductions = productions[A]
            # B is each production list
            for B in AsProductions:
                print "\n"
                print "A: " + IDToSymb[A]

                # If there's a Bi in T U NT, so I think just not empty or EOF
                if len(set(B).intersection(allSymbs)) > 0:
                    print "In here!"

                    # Make rhs = all first's of b0->bn where all b0->bn-1 have epsilon in firsts, i.e. could be empty
                    rhs = FIRST[B[0]].difference(set([EPSILON]))
                    print "Len rhs: " + str(len(rhs))
                    i = 0
                    # means if FIRST[B[i]].contains(EPSILON) and B[i} exists:
                    while len(FIRST[B[i]].intersection(set([EPSILON]))) > 0 and i < len(B) - 1:
                        i += 1
                        rhs = rhs.union(FIRST[B[i]].difference(set([EPSILON])))
                    # TODO: Check, I assume we're actually supposed to have these 2 statements inside
                    # the if, but not sure.  I isn't defined out there so idk what that would even mean

                    # If all up to the last produced element in B could be empty, empty is a valid first
                    # Like above, means if FIRST[B[i]].contains(EPSILON):
                    if i == len(B) - 1 and len(FIRST[B[i]].intersection(set([EPSILON]))) > 0:
                        rhs.add(EPSILON)

                    # Update FIRSTS to include the possible RHS's from this production IF THEYVE CHANGED
                    possibleNewFirsts = FIRST[A].union(rhs)
                    if len(possibleNewFirsts) != len(FIRST[A]):
                        changing=True
                        FIRST[A] = possibleNewFirsts

            #TODO: Check that first sets changed this iteration
            # TODO: Thought, just change to false at start of it, make true inside of if statement?
    return FIRST

# Need to factor in EPSILON somehow, since it's important for productions but not a symbol
# (Unlike DERIVES or ALSODERIVES, which are implied by the structure of the IR
# Current soln: Have IDToSymb just start out w/ it
def printProductions(prods, IDToSymb):
    for nonTerm in prods:
        print "Nonterminal " + IDToSymb[nonTerm] + " produces:"
        for production in prods[nonTerm]:
            rhsStr = "\t"
            for symbol in production:
                rhsStr += IDToSymb[symbol] + " "
            print rhsStr

def printSymbSet(mySet, mapping):
    retStr = "("
    for el in mySet:
        retStr += mapping[el] + ", "
    print retStr[:-2] + ")"

"""
Main functionality to build the table
"""

# Use MBNF parser to verify example grammar is valid, get productions
# Current IR: {NonTerm1 : [NT1Prod1, NT1Prod2, ...]; NonTerm2 : [...]; ...}
# W/ ^, keyset is nonterminals, can access productions by NonTerminal ID

productions = parseFile("factor.ll1")
symbToID = getSymbolsToIDs()
IDToSymb = getIDsToSymbols()

print "Productions: "
printProductions(productions, IDToSymb)

# Everything uses id's, only use symbols for printing
nonTerminals = set()
for key in productions:
    nonTerminals.add(key)

print "\nNonterminals: "
printSymbSet(nonTerminals, IDToSymb)

allSymbs = set()
for key in IDToSymb:
    allSymbs.add(key)
terminals = allSymbs.difference(nonTerminals)
#Need to remove EPSILON and EOF for building tables
terminals.remove(EPSILON)

print "\nTerminals: "
printSymbSet(terminals, IDToSymb)

firsts = getFirsts(nonTerminals, terminals, productions, IDToSymb)

print "Found firsts: "
printFirsts(firsts, IDToSymb)