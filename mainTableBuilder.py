from mbnfParser import parseFile
from scanner import getSymbolsToIDs, getIDsToSymbols

SEMICOLON=1
DERIVES=2
ALSODERIVES=3
EPSILON=4
SYMBOL=5
EOF=6
ERROR = -1

def printTable(t, IDToSymb, terms):
    termsOrdered = list(terms)
    #TODO: Need to append EOF probably
    IDToSymb[ERROR] = '--'

    print "table:"
    for nt in t:
        prStr = IDToSymb[nt] + ": {"
        for term in termsOrdered:
            prStr += IDToSymb[term]
            if t[nt][term] == ERROR:
                prStr += ": --, "
            else:
                prStr += ": " + str(t[nt][term]) + ", "
        print prStr[:-2] + "}"


def getTable(nonTerminals, terminals, firstPlus):
    Table = {}
    for A in nonTerminals:
        Table[A] = {}
        # TODO: Need to do terminals + EOF?
        for w in terminals:
            Table[A][w] = ERROR

        for producedByAID in firstPlus[A]:
            #TODO: I think these should all actually be terminals, but maybe need to check
            for w in firstPlus[A][producedByAID]:
                Table[A][w] = producedByAID
            # I think we've got that covered
            #if eof

    return Table


def printFirstPlus(firstPlus, productionsOrdered, IDToSymb):
    for i in range(len(productionsOrdered)):
        curProd = productionsOrdered[i]
        prStr = str(i) + " : " + IDToSymb[curProd[0]] + " -> "
        for bI in curProd[1:]:
            prStr += IDToSymb[bI] + ", "
        print prStr
        prStr = "\t"
        for fpSymb in firstPlus[curProd[0]][i]:
            prStr += IDToSymb[fpSymb] + ", "
        print prStr

def printProductionsOrdered(productionsOrdered, IDToSymb):
    for i in range(len(productionsOrdered)):
        thisProd = productionsOrdered[i]
        printStr = str(i) + ": {" + IDToSymb[thisProd[0]] + ": ["
        for j in range(len(thisProd) - 1):
            printStr += IDToSymb[thisProd[1+j]] + ", "
        print printStr[:-2] + "]}"

# First+ of form: {A:{B:(nt1, nt2, ...), B2:(...
# (Sets, not lists.  Not problematic tho, only productions care about ordering)

# New issue: what does firstplus of B mean?  Is it for entire production, or just first element?
def getFirstPlus(productionsOrdered, FIRST, FOLLOW, nonTerminals):
    FIRSTPLUS = {}
    for nt in nonTerminals:
        FIRSTPLUS[nt] = {}

    for i in range(len(productionsOrdered)):
        Oprod = productionsOrdered[i]
        A = Oprod[0]
        B = Oprod[1:]

        if not EPSILON in B:
            #Q: How to get FIRST[B] where B=B1,B2,B3,...
            #TODO: BIG assumption, saying FIRST[B] = FIRST[B0]
            FIRSTPLUS[A][i] = FIRST[B[0]]
        else:
            FIRSTPLUS[A][i] = FIRST[B[0]].union(FOLLOW[A])

    return FIRSTPLUS

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

                        if(IDToSymb[B[i]]=='Stmt'):
                            print "Setting for stmt:"
                            print "Trailer"

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

# Factor is good, simple candidate
#parens-alt has people posting their solns tho, so idk...
productions = parseFile("parens-alt.ll1")
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


# Number productions, pass in numbering to getFirstPlus
productionsOrdered = []
for A in productions:
    for prod in productions[A]:
        # Now each production A->B1B2B3 looks like [A,B1,B2,...]
        productionsOrdered.append([A] + prod)

print "Productions ordered: "
printProductionsOrdered(productionsOrdered, IDToSymb)

firstPlus = getFirstPlus(productionsOrdered, firsts, follows, nonTerminals)
#print "Found first plus set: "
#printFirstPlus(firstPlus, productionsOrdered, IDToSymb)

# TODO: Make table
t = getTable(nonTerminals, terminals, firstPlus)
printTable(t, IDToSymb, terminals)
