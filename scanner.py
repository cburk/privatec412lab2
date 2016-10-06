SEMICOLON=1
DERIVES=2
ALSODERIVES=3
EPSILON=4
SYMBOL=5
EOF=6

file = None

symbolToID = {}
nextID = 30

def openFile(fileName):
    global file
    file = open(fileName, 'r')

def readNextWord():
    global file
    global symbolToID
    global nextID

    thisChar = "asdf"
    while thisChar:
        thisChar = file.read(1)
        if thisChar == '':
            return EOF

        if thisChar == ' ' or thisChar == '\n' or thisChar == '    '  or thisChar == '\t':
            #print "Found whitespace"
            continue

        if thisChar == ';':
            return SEMICOLON
        elif thisChar == ':':
            return DERIVES
        elif thisChar == '|':
            return ALSODERIVES
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
                                    return EPSILON
            print "Expected epsilon, spelled incorrectly"
            return -1
        # TODO: pull out of while?
        elif thisChar == '':
            return EOF
        # Symbol path
        elif (ord(thisChar) >= 48 and ord(thisChar) <= 57) or (ord(thisChar) >= ord('A') and ord(thisChar) <= ord('Z')) or (ord(thisChar) >= ord('a') and ord(thisChar) <= ord('z')):
            symbolName = thisChar
            thisChar = file.read(1)
            while (ord(thisChar) >= 48 and ord(thisChar) <= 57) or (ord(thisChar) >= ord('A') and ord(thisChar) <= ord('Z')) or (ord(thisChar) >= ord('a') and ord(thisChar) <= ord('z')):
                symbolName += thisChar
                thisChar = file.read(1)

            # Keep track of symbol names w/ hashmap, as we interpret A-2. instr to mean
            if not symbolName in symbolToID:
                symbolToID[symbolName] = nextID
                nextID += 1

            print "Scanner found symbol: " + symbolName

            return SYMBOL
        else:
            return -1

def getSymbolsToIDs():
    global symbolToID
    return symbolToID