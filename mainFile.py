from scanner import openFile, readNextWord, getSymbolsToIDs

SEMICOLON=1
DERIVES=2
ALSODERIVES=3
EPSILON=4
SYMBOL=5
EOF=6

symbolNames = ["NONE/ERROR", "SEMICOLON", "DERIVES", "ALSODERIVES", "EPSILON", "SYMBOL", "EOF"]

nonterms=[1, 2, 3]
symbolPending = None

# For debugging only
testGrammerSymbols = [SYMBOL, DERIVES, SYMBOL, SYMBOL, SYMBOL, ALSODERIVES, SYMBOL, SYMBOL, ALSODERIVES, SYMBOL, SEMICOLON, SYMBOL, DERIVES, SYMBOL, SYMBOL, ALSODERIVES, SYMBOL, SYMBOL, SYMBOL, SEMICOLON, EOF]
i = 0

def getNextWord():
    global symbolPending
    global testGrammerSymbols
    global i

    #Be sure to check queue before asking scanner
    if symbolPending:
        retSym = symbolPending
        symbolPending = None
        print "Returning: " + symbolNames[retSym]
        return retSym
    else:
        #         Debugging only
        """
        retSym = testGrammerSymbols[i]
        i = i + 1
        print "Returning: " + symbolNames[retSym]
        return retSym
        """
        return readNextWord()

    return 1

def SymbolList(curWord):
    """
    SL->SYMBOL SL
        | E
    Not what would be produced w/ the algorithm, but very obviously
    equivalent
    """
    global symbolPending

    if curWord == SYMBOL:
        return SymbolList(getNextWord())

    print "Sym list: " + symbolNames[curWord]

    # Empty case, has to be the start of another list or ;
    if curWord == SEMICOLON or curWord == ALSODERIVES:
        symbolPending = curWord
        return True


def RightHandSide(curWord):
    """
    RHS->SL
        | EPSILON
    """
    global symbolPending

    print "RHS, cur: " + symbolNames[curWord]

    return curWord == EPSILON or SymbolList(curWord)

    return True

def ProductionSetPrime(curWord):
    """
    PS'->ALSODERIVES RHS PS'
        | E
    """
    global symbolPending

    if curWord == ALSODERIVES:
        if RightHandSide(getNextWord()):
            return ProductionSetPrime(getNextWord())
        else:
            return False
    print "empty case: " + symbolNames[curWord]
    # Empty case, if no other things being derived, should be a SEMICOLON
    if curWord == SEMICOLON:
        symbolPending = curWord
        return True

def ProductionSet(curWord):
    """
    PS->SYMBOL DERIVES RHS PS'
    """
    global symbolPending

    if curWord == SYMBOL:
        if getNextWord() == DERIVES:
            if RightHandSide(getNextWord()):
                return ProductionSetPrime(getNextWord())
    return False


def ProductionListPrime(curWord):
    """
    PL'->PS SEMICOLON PL'
        | E
    """
    global symbolPending

    if(ProductionSet(curWord)):
        if getNextWord() != SEMICOLON:
            return False
        return ProductionListPrime(getNextWord())

    # Empty case, last item of full list is EOF
    return curWord == EOF

def ProductionList(curWord):
    """
    PL->PS SEMICOLON PL'
    """
    global symbolPending

    if not ProductionSet(curWord):
        return False
    if getNextWord() != SEMICOLON:
        return False
    return ProductionListPrime(getNextWord())


def Grammar():
    global symbolPending

    return ProductionList(getNextWord())


openFile("sampleGrammar")
print Grammar()
print getSymbolsToIDs().keys()

#print "hello wrorld"
#print ProductionList(getNextWord())