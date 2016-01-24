#TO DO: Implement this.
#If RangeWorks is not around, we are going to use this to get a user defined size for our table.
#More important TODO:
#Take a file for input and use advanced options like having hyperlinks and images.
#(Images as in a URL reference to an image!)
#Maybe even move the images to a folder for easy uploading...

def staticSize():
    pass

try:
    from RangeWorks import collectionSize as sizeGen
except ImportError:
    print("No RangeWorks found. Alternative not implemented yet.")
    raise Exception("Can not generate table without RangeWorks.\n");
    #sizeGen = None

class TableGen:
    """This class is a quick and dirty HTML table generator. It uses either a list of rows or a list of columns to generate a simple html table."""
    #Quick HTML Table Generator
    TABLE_TEMPLATE = "<table> {0} \n</table>"
    ROW_TEMPLATE = "\n<tr> {0} \n</tr>"
    COLUMN_TEMPLATE = '\n\t<td align="center">{:^20}</td>'
    
    def __init__(self, defaultForEmpty = ''):
        self.default = defaultForEmpty
    
    #Regardless of whether the table is made rowByRow 
    #or columnByColumn, at the end of the day, both are
    #expecting a list something like:
    #    If rowByRow:
    #    [ [row1 Value1,row1 Value2, row1 Value3], [row2 Value1, row2 Value2, row2 Value3], [row3 Value1, row3 Value2, row3 Value3] ]
    #    If columnByColumn:
    #    [ [col1 Value1,col1 Value2, col1 Value3], [col2 Value1, col2 Value2, col2 Value3], [col3 Value1, col3 Value2, col3 Value3] ]

    #Generates the table row by row.
    #e.g. Asks in order:
    # [1,2]
    # [3,4]
    # [5,6]
    def rowByRow(self, rowList):
        """Given a list of rows, this will return a list of padded, evenly sized rows."""
        tableDimensions = sizeGen(rowList)
        rowNumber = tableDimensions[0]
        columnNumber = tableDimensions[1][0]
        default = [self.default]
        
        newRowList = []
        
        #We need to pad any rows that are not the same size to be of the same size.
        #To do this, we use the default value.
        for row in rowList:
            if isinstance(row, str):
                #This is a row wide value so we create a list with only this value across the whole thing.
                tempList = [row] * (columnNumber)
            elif len(row) < columnNumber:
                #This particular row is a bit on the small side, so we need to pad it.
                tempList = row + default * ( columnNumber - len(row) )
            else:
                tempList = list(row)
            newRowList.append(tempList)
        
        return newRowList
        
    #Generates the table by columns instead.
    #e.g Asks in order:
    # [1,4]
    # [2,5]
    # [3,6]
    def columnByColumn(self, columnList):
        """Given a list of columns, this will return a list of padded, evenly sized rows."""
        tableDimensions = sizeGen(columnList)
        columnNumber = tableDimensions[0]
        rowNumber = tableDimensions[1][0]
        print(rowNumber)
        default = [self.default]
        #In theory we could modify the existing list in place, but because
        #of the strings used for column wide values, we need to create a new list (alternatively we could insert new lists in place).
        
        newColList = []
        #We need to pad any columns that are not the same size to be of the same size.
        #To do this, we use the default value.
        for column in columnList:
            if isinstance(column, str):
                #This is a column wide value so we create a list with only this value across the whole thing.
                tempList = [column] * (rowNumber)
            elif len(column) < rowNumber:
                #This particular column is a bit on the small side, so we need to pad it.
                tempList = column + default * ( rowNumber - len(column) )
            else:
                tempList = list(column)
            newColList.append(tempList)
        
        #Now we take our list of columns and turn it into a list of rows.
        #http://stackoverflow.com/q/6473679
        rowList = list(zip(*newColList))
        return rowList
        
    def turnIntoTable(self, rows):
        """Expects a list of rows. This will turn them into a table."""
        colTemplate = self.COLUMN_TEMPLATE
        rowTemplate = self.ROW_TEMPLATE
        tableTemplate = self.TABLE_TEMPLATE
        
        finalizedRows = []
        for row in rows:
            tempList = [ colTemplate.format( x ) for x in row ]
            finalizedRows.append( rowTemplate.format( ''.join(tempList) ) )
        finalTable = tableTemplate.format(''.join(finalizedRows))
        return finalTable
    
def getInput():
    """
    This returns a list of the following format:
    [ [], [], [] ]
    The list parameters that are part of this list are either representative of rows or columns.
    e.g. If rowByRow calls us, we get:
    [ [row1 Value1,row1 Value2, row1 Value3], [row2 Value1, row2 Value2, row2 Value3], [row3 Value1, row3 Value2, row3 Value3] ]
    e.g. If columnByColumn calls us, we get:
    [ [col1 Value1,col1 Value2, col1 Value3], [col2 Value1, col2 Value2, col2 Value3], [col3 Value1, col3 Value2, col3 Value3] ]
    """
    print("Enter C for column based creation or R for row based creation or q to quit.")
    columnBased = False
    while True:
        userInput = input('->')
        if userInput.upper() == "Q":
            print("Exiting")
            return
        if userInput.upper() == "C":
            print("Column Based Run")
            columnBased = True
            break
        elif userInput.upper() == "R":
            print("Row Based Run")
            columnBased = False
            break
            
    inputRules = \
    """
Input Rules:
    Every input counts as a row or a column.
    Special Characters:
        \q : Quit
        \\n : Next Column or Row (depending on which one you are doing)
        \d : Goes to the next column or Row and takes the next input (entered after \d) as a default input for the entire row or the entire column.
    """
    print(inputRules)
    retList = []
    userInput = "dummy"
    curItem = []
    #There are two possibilities here.
    #Either the user enters the table line by line
    #or they copy paste from another file.
    #We need to handle the two cases differently.
    #With a better implementaion, we wouldn't need to, but no!
    while userInput != "\q":
        userInput = input('->')
        temp = userInput.split('\n') #Get input line by line.
        if (len(temp) > 1):
            #We make the assumption that they have only entered data.
            #That is to say, we don't have special things like \d or \\n here.
            #We also make the assumption that any malformed things (like a single space)
            #are intentionally there.
            print( "Got several lines of input" )
            #print( temp )
            curItem = temp.copy();
        else:
            if userInput == "\\n" or userInput == "\n":
                retList.append(curItem)
                print("Moved to the next row/column.")
                curItem = []
            elif userInput == "\d":
                print("Moved to the next row/column. Enter a default value for this row or column.")
                retList.append(curItem)
                curItem = []
                userInput = input('->')
                if userInput == "\q": break
                #We append nothing but a single string for the case where we have a default value.
                #This is a bit ugly because later on we have to do an explicit check.
                retList.append(userInput)
                print("Moved to the next row/column.")
            elif userInput == "\q":
                if curItem:
                    retList.append(curItem)
                break
            else:
                curItem.append(userInput)

    tblGen = TableGen()
    
    if columnBased:
        print( tblGen.turnIntoTable( tblGen.columnByColumn(retList) ) )
    else:
        print( tblGen.turnIntoTable( tblGen.rowByRow(retList) ) )
        
    return retList
        
if __name__ == '__main__':
    userInput = "t"
    while userInput != "q":
        if userInput == "t":
            x = getInput()
            print(x)
        print( "Enter q to quit, t to print another table." )
        userInput = input('->')
