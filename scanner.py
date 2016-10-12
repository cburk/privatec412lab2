SEMICOLON=1
DERIVES=2
ALSODERIVES=3
EPSILON=4
SYMBOL=5
EOF=6

file = None

symbolPending = False
whichSymbol = ""


# Map between symbol names and an int representation, as per lab 2 slide 8
symbolToID = {}
IDToSymbol={}
nextID = 30

def openFile(fileName):
    global file
    file = open(fileName, 'r')

def readNextWord():
    global symbolPending
    global whichSymbol
    global file
    global symbolToID
    global nextID

    thisChar = "asdf"
    while thisChar:
        # SYMBOL path can read one over the end, need to keep track
        if symbolPending:
            thisChar = whichSymbol
            symbolPending = False
        else:
            thisChar = file.read(1)

        if thisChar == '':
            return [EOF, EOF]

        if thisChar == ' ' or thisChar == '\n' or thisChar == '    '  or thisChar == '\t':
            #print "Found whitespace"
            continue

        if thisChar == ';':
            return [SEMICOLON, SEMICOLON]
        elif thisChar == ':':
            return [DERIVES, DERIVES]
        elif thisChar == '|':
            return [ALSODERIVES, ALSODERIVES]
        elif thisChar == 'E' or thisChar == 'e':
            thisChar = file.read(1)
            if thisChar == 'P' or thisChar == 'p':
                thisChar = file.read(1)
                if thisChar == 'S' or thisChar == 's':
                    thisChar = file.read(1)
                    if thisChar == 'I' or thisChar == 'i':
                        thisChar = file.read(1)
                        if thisChar == 'L' or thisChar == 'l':
                            thisChar = file.read(1)
                            if thisChar == 'O' or thisChar == 'o':
                                thisChar = file.read(1)
                                if thisChar == 'N' or thisChar == 'n':
                                    return [EPSILON, EPSILON]
            print "Expected epsilon, spelled incorrectly"
            return -1
        # TODO: pull out of while?
        elif thisChar == '':
            return [EOF, EOF]
        # Symbol path
        elif (ord(thisChar) >= 48 and ord(thisChar) <= 57) or (ord(thisChar) >= ord('A') and ord(thisChar) <= ord('Z')) or (ord(thisChar) >= ord('a') and ord(thisChar) <= ord('z')):
            symbolName = thisChar
            thisChar = file.read(1)
            while (ord(thisChar) >= 48 and ord(thisChar) <= 57) or (ord(thisChar) >= ord('A') and ord(thisChar) <= ord('Z')) or (ord(thisChar) >= ord('a') and ord(thisChar) <= ord('z')):
                symbolName += thisChar
                thisChar = file.read(1)

            # If the character after a symbol is important, have to keep track of it
            symbolPending = True
            whichSymbol = thisChar

            # Keep track of symbol names w/ hashmap, as we interpret A-2. instr to mean
            if not symbolName in symbolToID:
                symbolToID[symbolName] = nextID
                IDToSymbol[nextID] = symbolName
                nextID += 1

            print "Scanner found symbol: " + symbolName

            return [nextID - 1, SYMBOL]
        else:
            return -1

def getSymbolsToIDs():
    global symbolToID
    return symbolToID

def getIDsToSymbols():
    global IDToSymbol
    return IDToSymbol