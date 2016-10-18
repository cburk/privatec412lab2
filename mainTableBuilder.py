import sys
from mbnfParser import parseFile
from scanner import getSymbolsToIDs, getIDsToSymbols

SEMICOLON=1
DERIVES=2
ALSODERIVES=3
EPSILON=4
SYMBOL=5
EOF=6
ERROR = -1

# TODO: New rule: terminals doesn't include EOF ever

def printTable(t, IDToSymb, terms):
    termsOrdered = list(terms)
    termsOrdered.append(EOF)

    #TODO: Need to append EOF probably
    IDToSymb[ERROR] = '--'

    print "table:"
    for nt in t:
        prStr = "  " + IDToSymb[nt] + ": {"
        for term in termsOrdered:
            prStr += IDToSymb[term]
            if t[nt][term] == ERROR:
                prStr += ": --, "
            else:
                prStr += ": " + str(t[nt][term]) + ", "
        print prStr[:-2] + "}"


def getTable(nonTerminals, terminals, firstPlus, IDToSymb):
    Table = {}
    for A in nonTerminals:
        Table[A] = {}
        # TODO: Need to do terminals + EOF?
        for w in terminals.union(set([EPSILON])):
            Table[A][w] = ERROR
            Table[A][EOF] = ERROR

        for producedByAID in firstPlus[A]:
            #TODO: I think these should all actually be terminals, but maybe need to check
            for w in firstPlus[A][producedByAID]:
                # If there are two productions from A w/ same first, we won't know which to do, i.e. needs lookahead of 2.
                # Error
                if Table[A][w] != ERROR:
                    sys.stderr.write("Error! Grammar not ll1, " + IDToSymb[A] + " produces " + IDToSymb[w] + " in productions " + str(producedByAID) + " and " + str(Table[A][w]) + "\n")
                    exit()

                Table[A][w] = producedByAID
                # I think we've got that covered
                #if EOF in firstPlus[A][producedByAID]:
                #   Table[A][EOF] = producedByAID

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
    print "productions:"
    for i in range(len(productionsOrdered)):
        thisProd = productionsOrdered[i]
        printStr = "  " + str(i) + ": {" + IDToSymb[thisProd[0]] + ": ["
        if thisProd[1] == EPSILON:
            print printStr + "]}"
        else:
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

        if not EPSILON in FIRST[B[0]]:
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


def getFirsts(nonTerminals, terminals, productions, IDToSymb):
    FIRST = {}
    # Change: I don't think this should include EOF or epsilon
    allSymbs = terminals.union(nonTerminals)

    for a in terminals.union(set([EPSILON, EOF])):
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
                #print "Firsts for nonterminal " + IDToSymb[A] + " cur producing:"
                #rhsStr = "\t"
                #for symbol in B:
                #    rhsStr += IDToSymb[symbol] + " "
                #print rhsStr

                debugzz = False
                #if IDToSymb[A] == "Factor":
                #print "Setting A's firsts"
                #debugzz = True

                # If there's a Bi in T U NT, so I think just not empty or EOF
                i = 1
                if len(set(B).intersection(allSymbs)) > 0:
                    # Make rhs = all first's of b0->bn where all b0->bn-1 have epsilon in firsts, i.e. could be empty
                    rhs = FIRST[B[0]].difference(set([EPSILON]))
                    if debugzz:
                        print "RHS After B[0] of " + IDToSymb[B[0]]
                        printSymbSet(rhs, IDToSymb, "RHS")
                        print "Epsilon in firsts of B[0]? " + str(EPSILON in FIRST[B[0]])

                    # means if FIRST[B[i]].contains(EPSILON) and B[i} exists:
                    while i < len(B) and len(FIRST[B[i-1]].intersection(set([EPSILON]))) > 0:
                        if debugzz:
                            print "Epsilon in last guy's firsts, gotta add more"
                        rhs = rhs.union(FIRST[B[i]].difference(set([EPSILON])))
                        i += 1
                        # TODO: Check, I assume we're actually supposed to have these 2 statements inside
                        # the if, but not sure.  I isn't defined out there so idk what that would even mean

                # If all up to the last produced element in B could be empty, empty is a valid first
                # Like above, means if FIRST[B[i]].contains(EPSILON):
                # Alternatively, now also means if this production is just epsilon
                if i == len(B) and len(FIRST[B[i - 1]].intersection(set([EPSILON]))) > 0:
                    rhs.add(EPSILON)

                # Update FIRSTS to include the possible RHS's from this production IF THEYVE CHANGED
                possibleNewFirsts = FIRST[A].union(rhs)
                if len(possibleNewFirsts) != len(FIRST[A]):
                    if debugzz:
                        printSymbSet(FIRST[A], IDToSymb, "First Before")
                        printSymbSet(possibleNewFirsts, IDToSymb, "Possible News")
                        print "\n"
                    changing=True
                    FIRST[A] = possibleNewFirsts

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

def printSymbSet(mySet, mapping, setName):
    retStr = setName + ": ["
    if len(mySet) == 0:
        print retStr + " ]"
        return
    for el in mySet:
        retStr += mapping[el] + ", "
    print retStr[:-2] + "]"

"""
Main functionality to build the table
"""

# Use MBNF parser to verify example grammar is valid, get productions
# Current IR: {NonTerm1 : [NT1Prod1, NT1Prod2, ...]; NonTerm2 : [...]; ...}
# W/ ^, keyset is nonterminals, can access productions by NonTerminal ID

# Factor is good, simple candidate
#parens-alt has people posting their solns tho, so idk...
# Even better, sbn and iloc have sample tables online
sFlagPrinting = False
tFlagPrinting = False
debugging = False

if len(sys.argv) > 1:
    if sys.argv[1] == '-h':
        prStr = "Command Line Args: "
        prStr += "-h: Show help"
        prStr += "-t <filename>: produces a YAML formatted parsing table for the grammar specified in filename"
        prStr += "-s <filename>: outputs the first, follow, and first+ sets for the grammar specified in filename"
        print prStr
    if len(sys.argv) > 2:
        if sys.argv[1] == '-s':
            sFlagPrinting = True
        # Incorrect args, if none of the above
        if sys.argv[1] == '-t':
            tFlagPrinting = True
        else:
            sys.stderr.write("Error, incorrect arg: " + sys.argv[1])
            exit()
else:
    sys.stderr.write("Error, 0 args given")
    exit()

# debugging purposes, TODO: Commeknt out!
#sFlagPrinting = False
#tFlagPrinting = False

filename = sys.argv[2]
productions = parseFile(filename)

symbToID = getSymbolsToIDs()
IDToSymb = getIDsToSymbols()

# Number productions, pass in numbering to getFirstPlus
productionsOrdered = []
for A in productions:
    for prod in productions[A]:
        # Now each production A->B1B2B3 looks like [A,B1,B2,...]
        productionsOrdered.append([A] + prod)

#print "Productions ordered: "
#printProductionsOrdered(productionsOrdered, IDToSymb)

# Everything uses id's, only use symbols for printing
nonTerminals = set()
for key in productions:
    nonTerminals.add(key)

allSymbs = set()
for key in IDToSymb:
    allSymbs.add(key)
terminals = allSymbs.difference(nonTerminals)
#Need to remove EPSILON and EOF for building tables
terminals.remove(EPSILON)
terminals.remove(EOF)

goalSymbol = findGoalSymbol(productions, nonTerminals)
#print "\n\nFound goal symbol: " + IDToSymb[goalSymbol]

#print "Productions: "

firsts = getFirsts(nonTerminals, terminals, productions, IDToSymb)

if sFlagPrinting:
    print "===================\n\nFound firsts: \n\n===================\n"
    printFirsts(firsts, IDToSymb)

follows = getFollows(nonTerminals, terminals, productions, firsts, IDToSymb, goalSymbol)

if sFlagPrinting:
    print "===================\n\nFound follows: \n\n===================\n"
    printFirsts(follows, IDToSymb)


firstPlus = getFirstPlus(productionsOrdered, firsts, follows, nonTerminals)

if sFlagPrinting:
    print "===================\n\nFound first+: \n\n===================\n"
    printFirstPlus(firstPlus, productionsOrdered, IDToSymb)

# TODO: Make table
t = getTable(nonTerminals, terminals, firstPlus, IDToSymb)
if tFlagPrinting:
    #print "\nTerminals: "
    printSymbSet(terminals, IDToSymb, "terminals")
    #print "\nNonterminals: "
    printSymbSet(nonTerminals, IDToSymb, 'non-terminals')
    print "eof-marker: " + IDToSymb[EOF]
    print "error-marker: --"
    print "start-symbol: " + IDToSymb[goalSymbol] + "\n"

    printProductionsOrdered(productionsOrdered, IDToSymb)
    print ''
    printTable(t, IDToSymb, terminals)
