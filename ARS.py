#! /usr/bin/python3

from tkinter import *
import tkinter.messagebox as tm
import cx_Oracle

# import all the lower level applications for use with ARS
import apps.new_vehicle_registration as app1
import apps.auto_transaction as app2
import apps.driver_licence_registration as app3
import apps.violation_records as app4
import apps.search_engine as app5

# Holds the conenction to the DB for queries, etc
global_userCx = None

# Lets the user login to an Oracle DB account
def login():
    global global_userCx
    
    if global_userCx != None:
        tm.showerror( "Login Error", "You are already connected!" )
        return
        
    
    top = Toplevel()
    top.title( "Oracle Login" )
    top.resizable( width=FALSE, height=FALSE )
    
    #src: http://stackoverflow.com/questions/28156719/
    #     how-can-i-integrate-tkinter-with-python-log-in-screen
    # I applied it without an object however.
    
    label1 = Label( top, text="Username" )
    label2 = Label( top, text="Password" )
    
    entry1 = Entry( top )
    entry2 = Entry( top, show="*" )
    
    label1.grid( row=0, sticky=E )
    label2.grid( row=1, sticky=E )
    entry1.grid( row=0, column=1 )
    entry2.grid( row=1, column=1 )
    
    def performLogin():
        try:
            username = entry1.get()
            password = entry2.get()
            
            con_string = username + "/" + password +\
                         "@gwynne.cs.ualberta.ca:1521/CRS"
            
            global global_userCx
            global_userCx = cx_Oracle.connect( con_string )
            
            successInfo = "You have successfully connected to: " +\
                          global_userCx.dsn
            tm.showinfo( "Login Success", successInfo )  
            
            top.destroy()
            
        except:
            errMsg = "Check your username and password! \ner_nox02"
            tm.showerror( "Login Error", errMsg )
    
    loginButton = Button( top, text="login", command=performLogin )
    loginButton.grid( columnspan=2 )

# Allows override for exit button on ARS 
# (we close your connection if it's connected)
def disconnect():
    try:
        #print( "attempting to close:", global_userCx.dsn )
        global_userCx.close()
        #print( "close successful." )
    except:
        #print( "WARNING: Connection may not have terminated properly." )
        if global_userCx != None:
            errMsg = "Connection may not have terminated properly."
            tm.showerror( "WARNING!", errMsg )
        
    exit()

def main():
    # MAIN ===================================================================
    top = Tk()
    top.wm_title( "ARS" )
    top.resizable( width=FALSE, height=FALSE )
    top.geometry( '{}x{}'.format( 250, 365) )

    top.protocol( 'WM_DELETE_WINDOW', disconnect )

    # App1 ===================================================================
    info1 = "New Vehicle Registration:"
    msg1 = Message( top, text=info1, padx=5, pady=5, width=200 )
    msg1.pack()

    top.app1_button = Button( top, padx=5, pady=5, width=25 )
    top.app1_button["text"] = "Open"
    top.app1_button["command"] = lambda: app1.run( global_userCx )
    top.app1_button.pack( side="top" )

    # App2 ===================================================================
    info2 = "Auto Transaction:"
    msg2 = Message( top, text=info2, padx=5, pady=5, width=200 )
    msg2.pack()

    top.app2_button = Button( top, padx=5, pady=5, width=25 )
    top.app2_button["text"] = "Open"
    top.app2_button["command"] = lambda: app2.run( global_userCx )
    top.app2_button.pack( side="top" )

    # App3 ===================================================================
    info3 = "Driver Licence Registration:"
    msg3 = Message( top, text=info3, padx=5, pady=5, width=200 )
    msg3.pack()

    top.app3_button = Button( top, padx=5, pady=5, width=25 )
    top.app3_button["text"] = "Open"
    top.app3_button["command"] = lambda: app3.run( global_userCx )
    top.app3_button.pack( side="top" )

    # App4 ===================================================================
    info4 = "Violation Record:"
    msg4 = Message( top, text=info4, padx=5, pady=5, width=200 )
    msg4.pack()

    top.app4_button = Button( top, padx=5, pady=5, width=25 )
    top.app4_button["text"] = "Open"
    top.app4_button["command"] = lambda: app4.run( global_userCx )
    top.app4_button.pack( side="top" )

    # App5 ===================================================================
    info5 = "Search Engine:"
    msg5 = Message( top, text=info5, padx=5, pady=5, width=200 )
    msg5.pack()

    top.app5_button = Button( top, padx=5, pady=5, width=25 )
    top.app5_button["text"] = "Open"
    top.app5_button["command"] = lambda: app5.run( global_userCx )
    top.app5_button.pack( side="top" )

    # Login ===========================================================
    info6 = "-"*50
    msg6 = Message( top, text=info6, padx=5, pady=5, width=200 )
    msg6.pack()

    top.app6_button = Button( top, padx=5, pady=5, width=25 )
    top.app6_button["text"] = "Login"
    top.app6_button["command"] = login
    top.app6_button.pack( side="top" )

    top.mainloop()

if __name__ == "__main__":
    main()
