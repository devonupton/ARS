''' New Vehicle Registration Application '''

from tkinter import *
import cx_Oracle
import tkinter.messagebox as tm
import apps.tableWidget as tW
from apps.new_persons_application import NewPerson

#The application object for New Vehicle Registration
class App1( Toplevel ):
    def __init__( self, userCx ):
        Toplevel.__init__( self )
        self.title( "New Vehicle Registration Application" )
        self.userCx = userCx
        self.resizable( width=FALSE, height=FALSE )

        #Create and add widgets for vehicle info
        msgtext = "Vehicle Information"
        msg1 = Message( self, text=msgtext, padx=5, pady=5, width=200 )
        msg1.grid( row=0, sticky=N, columnspan=2 )

        vehicle_id_label= Label( self, text="Vehicle ID" )
        self.vehicle_id_entry = Entry( self )
        vehicle_id_label.grid( row=1, sticky=E )
        self.vehicle_id_entry.grid( row=1, column=1 )

        maker_label = Label( self, text="Maker" )
        self.maker_entry = Entry( self )
        maker_label.grid( row=2, sticky=E )
        self.maker_entry.grid( row=2, column=1 )

        model_label = Label( self, text="Model" )
        self.model_entry = Entry( self )
        model_label.grid( row=3, sticky=E )
        self.model_entry.grid( row=3, column=1 )

        year_label = Label( self, text="Year" )
        self.year_entry = Entry( self )
        year_label.grid( row=4, sticky=E )
        self.year_entry.grid( row=4, column=1 )

        color_label = Label( self, text="Color" )
        self.color_entry = Entry( self )
        color_label.grid( row=5, sticky=E )
        self.color_entry.grid( row=5, column=1 )

        type_id_label = Label( self, text="Type ID" )
        self.type_id_entry = Entry( self )
        type_id_label.grid( row=6, sticky=E )
        self.type_id_entry.grid( row=6, column=1 )

        #Create and add widgets for Personal info
        msgtext = "Personal Information"
        msg2 = Message( self, text=msgtext, padx=5, pady=5, width=200 )
        msg2.grid( row=0, column=2, sticky=N, columnspan=2 )

        primary_owner_id_label = Label( self, text="Primary Owner ID" )
        self.primary_owner_id_entry = Entry( self )
        primary_owner_id_label.grid( row=1, column=2, sticky=E )
        self.primary_owner_id_entry.grid( row=1, column=3 )

        owner_id_label = Label( self, text="Other Owner IDs" )
        self.owner_id_entry = Entry( self )
        owner_id_label.grid( row=2, column=2, sticky=E )
        self.owner_id_entry.grid( row=2, column=3 )

        owner_id_label2 = Label(self, text="(comma separated list of sin #'s)")
        owner_id_label2.grid( row=3, column=2, columnspan=2, )

        #Buttons
        type_id_help_button = Button( self, text="?", \
                    command=lambda: self.findVehicleTypes(), padx=0, pady=0 )
        type_id_help_button.grid( row=6, column=2, sticky=W )

        new_person_button = Button( self, text="Add new Person", \
                    command=lambda: NewPerson( self, self.autofill ) )
        new_person_button.grid( row=3, column=2, rowspan=3, columnspan=2, )

        submit_button = Button( self, text="Submit", \
                    command=lambda: self.submit_form() )
        submit_button.grid( row=5, column=2, rowspan=2, columnspan=2, )

    #Used to fill the sin # upon returning from NewPerson app
    def autofill( self, value ):
        if self.primary_owner_id_entry.get() == "":
            self.primary_owner_id_entry.insert( 0, value )
        elif self.owner_id_entry.get() == "":
            self.owner_id_entry.insert( 0, value )
        else:
            self.owner_id_entry.insert( END, ", " + value )

    #Returns a super table of vehicle types for the user
    def findVehicleTypes( self ):
        askMsg = "Do you wish to bring up a table of the possible " + \
                 "Vehicle Types and their Type IDs?"
        if not tm.askyesno( "Type ID Help", askMsg ):
            return
        
        cursor = self.userCx.cursor()
        
        statement = "SELECT UNIQUE * FROM vehicle_type"
        cursor.execute( statement )
        
        rows = cursor.fetchall()
        if len( rows ) == 0:
            msg = "There are no Vehicle Types in the database.\nErr 0xa1-18"
            tm.showerror( "No Vehicle Types!", msg )
            
        tW.buildSuperTable( cursor.description, rows, "Vehicle Types" )
        
        cursor.close()

    #Attempt to submit data to the database
    def submit_form( self ):

        #Get each input value
        self.entries = { "vehicle_id":  self.vehicle_id_entry.get().strip(),
                         "maker":       self.maker_entry.get().strip(),
                         "model":       self.model_entry.get().strip(),
                         "year":        self.year_entry.get(),
                         "color":       self.color_entry.get().strip(),
                         "type_id":     self.type_id_entry.get() }

        #Get owners and remove extra spaces
        self.primary_owner_id = self.primary_owner_id_entry.get().strip()
        self.owner_id_list = self.owner_id_entry.get().split( "," )
        for element in range(len(self.owner_id_list)):
            self.owner_id_list[element] = self.owner_id_list[element].strip()

        #Check if input is valid 
        if not self.validate_input():
            return
        msg = "Are you sure you want to submit?"
        if not tm.askyesno( "Submit Confirmation", msg ):
            return

        cursor = self.userCx.cursor()

        #Create query statments
        vehicle_statement = "INSERT INTO vehicle \
                             VALUES( :vehicle_id, :maker, :model, \
                             :year, :color, :type_id )"
        primary_owner_statement = "INSERT INTO owner \
                                   VALUES( :a, :b, 'y' )"
        secondary_owner_statement = "INSERT INTO owner \
                                     VALUES( :a, :b, 'n' )"

        error_type = "Submit Failure"

        #Create savepoint here
        cursor.execute( "SAVEPOINT App1Save" )

        #Try to insert Vehicle
        try:
            cursor.execute( vehicle_statement, self.entries )
        except cx_Oracle.DatabaseError as exc:
            cursor.execute( "ROLLBACK to App1Save" ) 
            cursor.close()
            error, = exc.args
            if error.code == 1: #Vehicle must already exist
                tm.showerror( error_type, "Vehicle ID '" + \
                    self.entries["vehicle_id"] + \
                    "' is already in the database\nErr 0xa1-9" )
            elif error.code == 2291: #type_id does not exist
                tm.showerror( error_type, "Type ID '" + \
                    str( self.entries["type_id"] ) + \
                    "' does not exist\nErr 0xa1-10" )
            else: #Unknown error
                tm.showerror( error_type, error.message + "\nErr 0xa1-11" )
            return

        #Try to insert Primary Owner
        try:
            cursor.execute( primary_owner_statement, a=self.primary_owner_id, \
                                                 b=self.entries["vehicle_id"] )
        except cx_Oracle.DatabaseError as exc:
            cursor.execute("ROLLBACK to App1Save" )
            cursor.close()
            error, = exc.args
            if error.code == 2291: #Owner ID does not exist
                tm.showerror( error_type, "Owner ID '" + \
                        self.primary_owner_id + "' does not exist\nErr 0xa1-12")
            else: #Unknown error
                tm.showerror( error_type, error.message + "\nErr 0xa1-13" )
            return

        #Try to insert other owners
        for owner_id in self.owner_id_list:
            try:
                cursor.execute( secondary_owner_statement, a=owner_id, \
                                b=self.entries["vehicle_id"] )
            except cx_Oracle.DatabaseError as exc:
                cursor.execute("ROLLBACK to App1Save" )
                cursor.close()
                error, = exc.args
                if error.code == 1: #Duplicate owner_id
                    tm.showerror( error_type, "Owner ID '" + owner_id + \
                                  "' entered more than once\nErr 0xa1-14" )
                elif error.code == 2291: #Owner ID does not exist
                    tm.showerror( error_type, "Owner ID '" + owner_id + \
                                  "' does not exist\nErr 0xa1-15" )
                else: #Unknown error
                    tm.showerror( error_type, error.message + "\nErr 0xa1-16" )
                return

        #SQL statements executed successfully
        cursor.close()
        self.userCx.commit()

        #Success message
        successInfo = "Vehicle '" + self.entries["vehicle_id"] + \
                      "' has been created\n" + \
                      "Primary Owner ID: " + self.primary_owner_id + "\n" + \
                      "Other Owner IDs: " + ", ".join(self.owner_id_list)
        tm.showinfo( "Success!", successInfo )  
        self.destroy()
            

    #Type checking
    def validate_input( self ):
        error_type = "Input Error"

        #vehicle_id validation
        if self.entries["vehicle_id"] == '' \
            or len( self.entries["vehicle_id"] ) > 15:
            msg = "Invalid Vehicle ID: Must not be blank and no longer " + \
                  "than 15 characters\nErr 0xa1-2" 
            tm.showerror( error_type, msg )
            return

        #maker validation
        if self.entries["maker"] == '' or len( self.entries["maker"] ) > 20:
            msg = "Invalid Maker: Must not be blank and no longer than 20 " + \
                  "characters\nErr 0xa1-3" 
            tm.showerror( error_type, msg )
            return
            
        #model validation
        if self.entries["model"] == '' or len( self.entries["model"] ) > 20:
            msg = "Invalid Model: Must not be blank and no longer than 20 " + \
                  "characters\nErr 0xa1-4" 
            tm.showerror( error_type, msg )
            return

        #year validation
        try:
            self.entries["year"] = int( self.entries["year"] )
            if not ( 0 <= self.entries["year"] < 10000 ):
                raise
        except:
            msg = "Invalid Year: Must be an integer between 0 and 9999" + \
                  "\nErr 0xa1-5" 
            tm.showerror( error_type, msg )
            return

        #color validation
        if self.entries["color"] == '' or len( self.entries["color"] ) > 10:
            msg = "Invalid Color: Must not be blank and no longer than 10 " + \
                  "characters\nErr 0xa1-6" 
            tm.showerror( error_type, msg )
            return

        #type_id validation
        try:
            self.entries["type_id"] = int( self.entries["type_id"] )
            if not ( -2147483648 <= self.entries["type_id"] < 2147483648 ):
                raise
        except:
            msg = "Invalid Type ID: Must be an integer between " + \
                  "-(2^31)-1 and (2^31)-1\nErr 0xa1-7" 
            tm.showerror( error_type, msg )
            return

        if self.owner_id_list == ['']:
            self.owner_id_list = []
        #owner_id validation
        for owner_id in self.owner_id_list + [self.primary_owner_id]:
            if owner_id == '' or len( owner_id ) > 15:
                msg = "Invalid Owner ID '" + owner_id + "': Must not be " + \
                      "blank or longer than 15 characters\nErr 0xa1-8"
                tm.showerror( error_type, msg )
                return

        #No errors encountered
        return True

#This function starts App1 if user is logged in
def run( userCx ):
    #Prevents use of app if user hasn't logged in.
    if userCx == None:
        msg = "You need to login before using this app.\nErr 0xa1-1"
        tm.showerror( "Error", msg )
        return
    App1( userCx )
    return
