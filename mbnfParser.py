from scanner import openFile, readNextWord, getSymbolsToIDs

SEMICOLON=1
DERIVES=2
ALSODERIVES=3
EPSILON=4
SYMBOL=5
EOF=6

symbolNames = ["NONE/ERROR", "SEMICOLON", "DERIVES", "ALSODERIVES", "EPSILON", "SYMBOL", "EOF"]

symbolPending = None

# Of form: {NonTerm1 : [NT1Prod1, NT1Prod2, ...]; NonTerm2 : [...]; ...}
productionsIR = {}

# For debugging only
testGrammerSymbols = [SYMBOL, DERIVES, SYMBOL, SYMBOL, SYMBOL, ALSODERIVES, SYMBOL, SYMBOL, ALSODERIVES, SYMBOL, SEMICOLON, SYMBOL, DERIVES, SYMBOL, SYMBOL, ALSODERIVES, SYMBOL, SYMBOL, SYMBOL, SEMICOLON, EOF]
i = 0

"""
Word pairs of the form: [grammaticalSymbol, lexeme]
"""
def getNextWord():
    global symbolPending
    global testGrammerSymbols
    global i

    #Be sure to check queue before asking scanner
    if symbolPending:
        retSym = symbolPending
        symbolPending = None
        #print "Returning: " + symbolNames[retSym[0]]
        return retSym
    else:
        #         Debugging only
        """
        retSym = testGrammerSymbols[i]
        i = i + 1
        return retSym
        """
        retSym = readNextWord()
        #print "Scanner gave us back: " + str(retSym)
        #print "Returning: " + symbolNames[retSym[0]]
        return retSym

    return 1


def SymbolList(curWord, listSoFar):
    global symbolPending
    global productionsIR

    """
    SL->SYMBOL SL
        | E
    Not what would be produced w/ the algorithm, but very obviously
    equivalent
    """
    if curWord[0] == SYMBOL:
        listSoFar.append(curWord[1])
        return SymbolList(getNextWord(), listSoFar)

    #print "Sym list: " + symbolNames[curWord[0]]

    # Empty case, has to be the start of another list or ;
    if curWord[0] == SEMICOLON or curWord[0] == ALSODERIVES:
        symbolPending = curWord
        return [True, listSoFar]


def RightHandSide(curWord):
    """
    RHS->SL
        | EPSILON
    """
    global symbolPending

    #print "RHS, cur: " + symbolNames[curWord[0]]

    # Need to return whether it's a valid RHS, and if so what the full RHS is
    if curWord[0] == EPSILON:
        return [True, [EPSILON]]
    thisList = []
    sl = SymbolList(curWord, thisList)
    if sl[0]:
        return sl

    return False

def ProductionSetPrime(curWord, nonTerm):
    """
    PS'->ALSODERIVES RHS PS'
        | E
    """
    global symbolPending

    if curWord[0] == ALSODERIVES:
        rhs = RightHandSide(getNextWord())
        if rhs[0]:
            # Add this production to IR
            productionsIR[nonTerm].append(rhs[1])
            return ProductionSetPrime(getNextWord(), nonTerm)
        else:
            return False
    #print "empty case: " + symbolNames[curWord[0]]
    # Empty case, if no other things being derived, should be a SEMICOLON
    if curWord[0] == SEMICOLON:
        symbolPending = curWord
        return True

def ProductionSet(curWord):
    """
    PS->SYMBOL DERIVES RHS PS'
    """
    global symbolPending

    if curWord[0] == SYMBOL:
        # Make entry for this non terminal in IR
        curNonTerm = curWord[1]
        productionsIR[curNonTerm] = []

        if getNextWord()[0] == DERIVES:
            # Expect RHS to return a tuple of [T/F, [symb1, symb2, symb3]]
            rhs = RightHandSide(getNextWord())
            if rhs[0]:
                # Add this rhs as a production of curNonTerm, have PS' do the same
                productionsIR[curNonTerm].append(rhs[1])
                return ProductionSetPrime(getNextWord(), curNonTerm)
    return False


def ProductionListPrime(curWord):
    """
    PL'->PS SEMICOLON PL'
        | E
    """
    global symbolPending

    if(ProductionSet(curWord)):
        if getNextWord()[0] != SEMICOLON:
            return False
        return ProductionListPrime(getNextWord())

    # Empty case, last item of full list is EOF
    return curWord[0] == EOF

def ProductionList(curWord):
    """
    PL->PS SEMICOLON PL'
    """
    global symbolPending

    if not ProductionSet(curWord):
        return False
    if getNextWord()[0] != SEMICOLON:
        return False
    return ProductionListPrime(getNextWord())


def Grammar():
    global symbolPending

    return ProductionList(getNextWord())


def parseFile(fileName):
    global productionsIR

    openFile(fileName)
    # If it's a valid grammar, return IR
    if Grammar():
        return productionsIR
    else:
        print "\n\nError! Parser found invalid grammar\n\n"
        return False



#openFile("mbnf.ll1")
#print Grammar()
#print getSymbolsToIDs().keys()

#print "hello wrorld"
#print ProductionList(getNextWord())