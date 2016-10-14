from mbnfParser import parseFile
from scanner import getSymbolsToIDs, getIDsToSymbols

SEMICOLON=1
DERIVES=2
ALSODERIVES=3
EPSILON=4
SYMBOL=5
EOF=6

def findGoalSymbol(productions, NT):
    candidates = NT
    for A in productions:
        for B in productions[A]:
            candidates = candidates.difference(set(B))
            if len(candidates) == 1:
                return candidates.pop()

    return "Error!"

#Convenience function, true if set A has B
def SetAContainsMemberB(A, B):
    return len(A.intersection(set([B]))) > 0

# S is the goal symbol, still need to find
def getFollows(nonTerminals, terminals, productions, FIRST, IDToSymb, S):
    FOLLOW = {}
    for A in nonTerminals:
        FOLLOW[A] = set()
    # TODO: critical assumption, goal (S) is a nonterminal.  Seems right tho...
    # Answer: yep, as per piazza it's just nonterm not on the right side of anything...
    FOLLOW[S].add(EOF)

    changing = True
    while changing:
        changing = False

        for A in productions:
            Bs = productions[A]
            for B in Bs:
                # Think this should be here, new trailer for
                # each of A's different productions
                TRAILER = FOLLOW[A]

                k = len(B)
                # Go over the individual symbols in each rhs r->l
                for i in range(k-1, -1, -1):
                    if SetAContainsMemberB(nonTerminals, B[i]):

                        possibleNewFollows = FOLLOW[B[i]].union(TRAILER)
                        if len(possibleNewFollows) != len(FOLLOW[B[i]]):
                            changing=True
                            FOLLOW[B[i]] = possibleNewFollows

                        #Equivalent to lines in algorithm
                        if SetAContainsMemberB(FIRST[B[i]], EPSILON):
                            TRAILER = TRAILER.union(FIRST[B[i]].difference(set([EPSILON])))
                        else:
                            TRAILER = FIRST[B[i]]

                    else:
                        TRAILER = set([B[i]])

    return FOLLOW

def printFirsts(firsts, IDToSymb):
    for symbol in firsts:
        firstStr = "[ "
        for symbolsFirsts in firsts[symbol]:
            firstStr += IDToSymb[symbolsFirsts] + " , "
        print IDToSymb[symbol] + " : " + firstStr[:-2] + "]"

#def printFollows(follows, IDToSymb):


#TODO: terminals shouldn't have EOF and EPSILON
#TODO: Also making assumption EPSILON = empty
def getFirsts(nonTerminals, terminals, productions, IDToSymb):
    FIRST = {}
    # ACTUAL TODO: might need to add in epsilon and eof
    allSymbs = terminals.union(nonTerminals).union(set([EPSILON]))

    # TODO: Should be terminals U EOF U epsilon
    for a in terminals.union(set([EPSILON])):
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

                # If there's a Bi in T U NT, so I think just not empty or EOF
                if len(set(B).intersection(allSymbs)) > 0:

                    # Make rhs = all first's of b0->bn where all b0->bn-1 have epsilon in firsts, i.e. could be empty
                    rhs = FIRST[B[0]].difference(set([EPSILON]))
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

print "===================\n\nFound firsts: \n\n===================\n"
printFirsts(firsts, IDToSymb)

goalSymbol = findGoalSymbol(productions, nonTerminals)
print "\n\nFound goal symbol: " + IDToSymb[goalSymbol]

follows = getFollows(nonTerminals, terminals, productions, firsts, IDToSymb, goalSymbol)
print "===================\n\nFound follows: \n\n===================\n"
printFirsts(follows, IDToSymb)

