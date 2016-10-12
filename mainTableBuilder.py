from mbnfParser import parseFile
from scanner import getSymbolsToIDs, getIDsToSymbols

SEMICOLON=1
DERIVES=2
ALSODERIVES=3
EPSILON=4
SYMBOL=5
EOF=6



# TODO: Need to factor in EPSILON somehow, since it's important for productions but not a symbol
# (Unlike DERIVES or ALSODERIVES, which are implied by the structure of the IR
# Thought: Have IDToSymb just start out w/ it
def printProductions(prods, IDToSymb):
    for nonTerm in prods:
        print "Nonterminal " + IDToSymb[nonTerm] + " produces:"
        for production in prods[nonTerm]:
            rhsStr = "\t"
            for symbol in production:
                rhsStr += IDToSymb[symbol] + " "
            print rhsStr


"""
Main functionality to build the table
"""

# Use MBNF parser to verify example grammar is valid, get productions
# TODO: Idea for IR: {NonTerm1 : [NT1Prod1, NT1Prod2, ...]; NonTerm2 : [...]; ...}
# W/ ^, keyset is nonterminals, can access productions by NonTerminal ID

productions = parseFile("iloc.ll1")
symbToID = getSymbolsToIDs()
IDToSymb = getIDsToSymbols()

print "Productions: "
printProductions(productions, IDToSymb)