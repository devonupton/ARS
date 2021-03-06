''' Search Engine Application '''
# This application allows a user to perform various searches in the 
# database that they are connected to. 
# You can see the major searches (there are three) detailed below. 
# The main component of this program is the "run" function.

from tkinter import *
import tkinter.messagebox as tm
import cx_Oracle
import apps.tableWidget as tW

global_lastType = None
global_lastString = None

#===============================================================================
# Function: checkLastSearch
#===============================================================================
# Maintains global variables to help warn the user if they are making 
# multiple of the same search in a row.
def checkLastSearch( searchType, strVar ):
    strVar = strVar.lower()
    global global_lastType
    global global_lastString

    if (searchType == global_lastType) and (strVar == global_lastString):
        yesnoMsg = "Your most recent search was '" + strVar +\
                   "' do you wish to search this again?"
        if tm.askyesno( "Double Search", yesnoMsg ):
            return True
        else:
            return False

    global_lastType = searchType
    global_lastString = strVar
    return True


#===============================================================================
# Function: searchone
#===============================================================================
# List the name, licence_no, addr, birthday, driving class,
# driving_condition, and the expiring_data of a driver by entering either 
# a licence_no or a given name. It shall display all the entries if a
# duplicate name is given.
def searchOne( userCx, strVar, isLicNo ):
        strVar = strVar.lower().strip()

        # Check if user input is empty
        if len( strVar ) < 1:
            type = "licence_no" if isLicNo else "Name"
            tm.showerror( "Invalid Input", "You need to specifiy a " +\
                          type + " to search!\nErr 0xa5-2" )
            return
           
        searchType = 11 if isLicNo else 12   
        if not checkLastSearch( searchType, strVar ):
            return

        # create the search title for the frame
        title = "licence_no" if isLicNo else "Name"
        title += " search on '" + strVar.lower() + "'"
        
        # build the SQL statement based on if it's a LicNo or a Name
        if isLicNo:
            statement = "SELECT P.name, L.licence_no, P.addr, P.birthday, " +\
                        "L.class, L.expiring_date " +\
                        "FROM People P LEFT JOIN drive_Licence L " +\
                        "ON P.sin = L.sin "+\
                        "WHERE LOWER(L.licence_no) = :a"
        else:
            statement = "SELECT P.name, L.licence_no, P.addr, P.birthday, " +\
                        "L.class, L.expiring_date " +\
                        "FROM People P LEFT JOIN drive_Licence L " +\
                        "ON P.sin = L.sin "+\
                        "WHERE LOWER(P.name) = :a"
            
        # open a cursor for database usage
        thisCursor = userCx.cursor()
        
        # try to execute the requested statement
        try:
            if isLicNo:
                thisCursor.execute( statement, a=strVar.lower().ljust(15) )
            else:
                thisCursor.execute( statement, a=strVar.lower() )
        except:
            errMsg = "There is a problem with the search, " +\
                     "please try again.\nErr 0xa5-3"
            tm.showerror( "Invalid Input", errMsg )
            return
         
        rows = thisCursor.fetchall()
        
        # If there was no results, it means 
        # the person wasn't in the database (LEFT JOIN)
        if len( rows ) == 0:
            infoMsg = title + " not found in database! Check " +\
                      "spelling and try again.\nErr 0xa5-11"
            tm.showerror( "No results!", infoMsg )
            return
    
        # build the tableSpace for tableWidget 
        numRows = len( rows )
        numCols = len( thisCursor.description )
        
        # get the header elements
        headerList = []
        for object in thisCursor.description:
            headerList.append( object[0] )
        # append the extra search for conditions
        headerList.append( "CONDITION(S)" )
        
        # start the tableSpace with the header row
        tableRows = [headerList]
        
        # loop through all the rows returned by fetchall
        for x in range( numRows ):
            tempRow = []
            for entry in rows[x]:
                # for every entry in each row, append it to the temporary row
                if entry == None:
                    # if entry is a NoneType, apply this value instead
                    tempRow.append( "N/A" )
                else:
                    tempRow.append( entry )
            # When a temporary row is complete, search for the 
            # conditions on that result.
            # Because of the LEFT JOIN, some licence may be NoneType
            if tempRow[1] == "N/A":
                tempRow.append( "N/A" )
                tableRows.append( tempRow )
                continue;
            statement = "SELECT DC.description " +\
                        "FROM restriction R, driving_condition DC " +\
                        "WHERE R.r_id = DC.c_id AND LOWER(R.licence_no) = :a"
            thisCursor.execute( statement, \
                                a=tempRow[1].strip().lower().ljust(15) )  
            conditions = thisCursor.fetchall()
            if len( rows ) == 0:
                # if no conditions found for the licence, append N/A value
                tempRow.append( "N/A" )
            else:
                # if conditions found, append them the final element of tempRow
                condStr = ""
                #print( conditions )
                for object in conditions:
                    condStr += object[0] + "\n"
                # take all but the last newline character of the condStr
                tempRow.append( condStr[ 0: len(condStr)-1 ] )
                    
            tableRows.append( tempRow )
        
        thisCursor.close()
        
        tW.buildCxTable( tableRows, title )
        
#===============================================================================
# Function: searchTwo
#===============================================================================
# List all violation records received by a person if  the drive licence_no or 
# sin of a person  is entered.
def searchTwo( userCx, strVar, isLicNo ):
    strVar = strVar.strip().lower()

    # Check if user input is empty
    if len( strVar ) < 1:
        type = "licence_no" if isLicNo else "Name"
        tm.showerror( "Invalid Input", "You need to specifiy a " +\
                       type + " to search!\nErr 0xa5-7" )
        return

    searchType = 21 if isLicNo else 22   
    if not checkLastSearch( searchType, strVar ):
        return

    searchType = "licence_no=" if isLicNo else "SIN="
    title = "Violation Search on " + searchType + "'" + strVar + "'"

    thisCursor = userCx.cursor()

    # Translate the LicNo into a sin
    if isLicNo:
        statement = "SELECT P.sin FROM drive_Licence L, People P " +\
        "WHERE P.sin = L.sin AND LOWER( L.licence_no ) = :a"

        thisCursor.execute( statement, a=strVar.ljust(15) )
        rows = thisCursor.fetchall()
        if len( rows ) == 0:
            errMsg = "The licence_no '" + strVar +\
                     "' was not found in the database.\nErr 0xa5-6"
            tm.showerror( "No result!", errMsg )
            return
        
        licNo = strVar
        strVar = rows[0][0]
        strVar = strVar.strip().lower()

    # search for tickets on the SIN (strVar)
    statement = "SELECT violator_no AS violatior_SIN, " +\
                "ticket_no, vehicle_id, office_no AS officer_ID, " +\
                "vdate, place, TT.vtype, TT.fine, descriptions " +\
                "FROM ticket, ticket_type TT " +\
                "WHERE ticket.vtype = TT.vtype AND LOWER( violator_no ) = :a"

    thisCursor.execute( statement, a=strVar.ljust(15) )
    rows = thisCursor.fetchall()
    #print( rows )
    
    # Check why no results were found
    if len( rows ) == 0:
        if checkSIN( strVar, userCx ):
            if isLicNo:
                infoMsg = "The LicNo '" + licNo +\
                          "' has no recorded violations."
            else:
                infoMsg = "The SIN '" + strVar +\
                          "' has no recorded violations."
            tm.showinfo( "No Violations!", infoMsg )
            return
        else:
            if isLicNo:
                # This case will never occur (?)
                errMsg = "The LicNo '" + licNo +\
                         "' was not found in the database. Maybe check " +\
                         "your spelling.\nErr 0xa5-8"
            else:
                errMsg = "The SIN '" + strVar +\
                         "' was not found in the database. Maybe check " +\
                         "your spelling.\nErr 0xa5-10"     
            tm.showerror( "Entry Not Found", errMsg )
            return
        
    # Build the header table 
    headerList = []
    for object in thisCursor.description:
        headerList.append( object[0] )
    
    # Build the tableSpace
    tableRows = [headerList]
    for x in range( len( rows ) ):
        tempRow = []
        for entry in rows[x]:
            if entry == None:
                tempRow.append( "N/A" )
            else:
                tempRow.append( entry )
        tableRows.append( tempRow )

    thisCursor.close()
    tW.buildCxTable( tableRows, title )

#===============================================================================
# Function: checkSIN
#===============================================================================
# returns TRUE if the SIN is in the database 
def checkSIN( strVar, userCx ):
    strVar = strVar.lower().strip()
    thisCursor = userCx.cursor()
    statement = "SELECT * FROM people WHERE LOWER(sin) = :a"
    try:
        thisCursor.execute( statement, a=strVar.ljust(15) )
    except:
        thisCursor.close()
        tm.showerror( "Unexpected Error", "An unexpected " +\
                      "error occured.\nErr 0xa5-9")
        
    rows = thisCursor.fetchall()
   
    if len( rows ) == 0:
        return False
    
    return True
        
        
#===============================================================================
# Function: searchThree
#===============================================================================
# Print out the vehicle_history, including 
    # the number of times that a vehicle has been changed hand, 
    # the average price, 
    # and the number of violations it has been involved 
# by entering the vehicle's serial number. 
def searchThree( userCx, vinVar ):
    vinVar = vinVar.lower().strip()

    if len( vinVar ) < 1:
            tm.showerror( "Invalid Input", "You need to specifiy a " +\
                          "VIN" + " to search!\nErr 0xa5-4" )
            return

    if not checkLastSearch( 3, vinVar ):
        return
    
    thisCursor = userCx.cursor()

    # Check if vehicle is in DB system
    statement = "SELECT * FROM vehicle WHERE LOWER( serial_no ) = :a"
    thisCursor.execute( statement, a=vinVar.ljust(15) )
    rows = thisCursor.fetchall()
    if len( rows ) == 0:
        errMsg = "'" + vinVar + "' was not found in the data base.\nErr 0xa5-5"
        tm.showerror( "Invalid Search", errMsg )
        return
            
    # get violation count
    statement = "SELECT COUNT( * ) FROM ticket WHERE LOWER( vehicle_id ) = :a"
    thisCursor.execute( statement, a=vinVar.ljust(15) )
    rows = thisCursor.fetchall()
    numViolations = rows[0][0]
    
    # get avg( sale ) and count( sale )
    statement = "SELECT AVG( price ), COUNT( * ) FROM auto_sale " +\
                "WHERE LOWER( vehicle_id ) = :a"
    thisCursor.execute( statement, a=vinVar.ljust(15) )
    rows = thisCursor.fetchall()
    avgPrice = rows[0][0]
    numSales = rows[0][1]
    
    title = "History For VIN=" + vinVar 
    headerList = [ 'VIN', 'VIOLATIONS', 'AVG SALE PRICE', 'SALES' ]
    valueList = [ vinVar, str( numViolations ),\
                  str( avgPrice ), str( numSales ) ]

    thisCursor.close()
    tW.buildCxTable( [headerList, valueList], title )
    

#===============================================================================
# Function: run
#===============================================================================
# creates the toplevel that holds the user's interface for app5. 
def run( userCx ):
    # prevents use of app if user hasn't logged in.
    if userCx == None:
        errMsg = "You need to login before using this app.\nErr 0xa5-1"
        tm.showerror( "Error", errMsg )
        return
    
    top = Tk()
    top.title( "Search Engine" )
    top.resizable( width=FALSE, height=FALSE )

    # Setting up the various searches
    # LIST1 ====================================================================
    info1 = "Search: License Information"
    msg1 = Message( top, text=info1, padx=5, pady=5, width=200 )
    msg1.grid( row=0, sticky=N, columnspan=2 )

    name_entry = Entry( top )
    name_entry.grid( row=1, column=0, sticky=EW )
    name_entry.insert( 0, "Enter a name here")
    
    licNo_entry = Entry( top )
    licNo_entry.grid( row=1, column=1, sticky=EW )
    licNo_entry.insert( 0, "Enter a licence_no here" )
    
    search1Name_button = Button( top, text="Search By Name", \
                                 command=lambda: searchOne( userCx, \
                                                            name_entry.get(), \
                                                            False ) )
    search1Name_button.grid( row=2, column=0, sticky=EW )
    
    search1LicNo_button = Button( top, text="Search By licence_no", \
                                  command=lambda: searchOne( userCx, \
                                                             licNo_entry.get(),\
                                                             True ) )
    search1LicNo_button.grid( row=2, column=1, sticky=EW )

    
    # LIST2 ====================================================================
    info2 = "Search: Violation Records"
    msg2 = Message( top, text=info2, padx=5, pady=5, width=200 )
    msg2.grid( row=3, sticky=N, columnspan=2 )

    sin_entry = Entry( top )
    sin_entry.grid( row=4, column=0, sticky=EW )
    sin_entry.insert( 0, "Enter a SIN here" )
    
    # Be weary, this name is similar to the other licNo_entry
    lic_entry = Entry( top )
    lic_entry.grid( row=4, column=1, sticky=EW )
    lic_entry.insert( 0, "Enter a licence_no here" )

    search2Name_button = Button( top, text="Search By SIN", \
                                 command=lambda: searchTwo( userCx, \
                                                            sin_entry.get(), \
                                                            False ) )
    search2Name_button.grid( row=5, column=0, sticky=EW )
    
    search2LicNo_button = Button( top, text="Search By licence_no", \
                                  command=lambda: searchTwo( userCx, \
                                                             lic_entry.get(), \
                                                             True ) )
    search2LicNo_button.grid( row=5, column=1, sticky=EW )

    # LIST3 ====================================================================
    info3 = "Search: Vehicle History"
    msg3 = Message( top, text=info3, padx=5, pady=5, width=200 )
    msg3.grid( row=6, sticky=N, columnspan=2 )

    vin_entry = Entry( top )
    vin_entry.grid( row=7, columnspan=2, sticky=EW )
    vin_entry.insert( 0, "Enter a VIN here" )

    searchVIN_button = Button( top, text="Search By VIN", \
                               command=lambda: searchThree( userCx, \
                                                            vin_entry.get() ) )
    searchVIN_button.grid( row=8, columnspan=2, sticky=EW )

    #mainloop
    mainloop()
