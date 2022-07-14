import tkinter as tk 
from tkinter import messagebox
from tkinter import ttk
from tkinter import *
from tkinter.ttk import *

import socket
import threading
import sqlite3

LARGE_FONT = ("verdana", 13,"bold")

HOST = "127.0.0.1"
PORT = 65432
HEADER = 64
FORMAT = "utf8"
DISCONNECT = "x"


#option
SIGNUP = "signup"
LOGIN = "login"
LOGOUT = "logout"


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(1)

def ConnectToDB():
    cursor = sqlite3.connect('test.db')
    cursor.execute('''CREATE TABLE IF NOT EXISTS ACCOUNT(username STRING PRIMARY KEY NOT NULL, password STRING NOT NULL)''')
    return cursor

def Insert_New_Account(user,password):
    cursor=ConnectToDB()
    cursor.execute("insert into ACCOUNT(username,password) values(?,?);",(user,password))
    cursor.commit()

def check_clientSignUp(username):
    con=sqlite3.connect('test.db')
    cur=con.cursor()
    cur.execute("select username from ACCOUNT")
    rows = cur.fetchall()
    for row in rows:
        parse=str(row)
        parse_check =parse[2:]
        parse= parse_check.find("'")
        parse_check= parse_check[:parse]
        if parse_check == username:
            return False
    return True

Live_Account=[]
ID=[]
Ad=[]

def Check_LiveAccount(username):
    for row in Live_Account:
        parse= row.find("-")
        parse_check= row[(parse+1):]
        if parse_check== username:
            return False
    return True

def Remove_LiveAccount(conn,addr):
    for row in Live_Account:
        parse= row.find("-")
        parse_check=row[:parse]
        if parse_check== str(addr):
            parse= row.find("-")
            Ad.remove(parse_check)
            username= row[(parse+1):]
            ID.remove(username)
            Live_Account.remove(row)
            conn.sendall("True".encode(FORMAT))

def check_clientLogIn(username, password):
    con=sqlite3.connect('test.db')
    cur=con.cursor()
    cur.execute("select username from ACCOUNT")
    rows = cur.fetchall()
    if Check_LiveAccount(username)== False:
        return 0
    
    for row in rows:
        parse=str(row)
        parse_check =parse[2:]
        parse= parse_check.find("'")
        parse_check= parse_check[:parse]
        if parse_check == username:
            cur.execute("select password from ACCOUNT where username=(?)",[username])
            parse= str(cur.fetchone())
            parse_check =parse[1:]
            print(parse)
            print(parse_check)
            parse= parse_check.find("'")
            print(parse)
            parse_check= parse_check[:-2]
            print(parse)
            print(parse_check)
            if password== parse_check:
                return 1
    return 2

def clientSignUp(sck, addr):

    user = sck.recv(1024).decode(FORMAT)
    print("username:--" + user +"--")

    sck.sendall(user.encode(FORMAT))

    pswd = sck.recv(1024).decode(FORMAT)
    print("password:--" + pswd +"--")


    #a = input("accepting...")
    accepted = check_clientSignUp(user)
    print("accept:", accepted)
    sck.sendall(str(accepted).encode(FORMAT))

    if accepted:
        Insert_New_Account(user, pswd)

        # add client sign up address to live account
        Ad.append(str(addr))
        ID.append(user)
        account=str(Ad[Ad.__len__()-1])+"-"+str(ID[ID.__len__()-1])
        Live_Account.append(account)

    print("end-logIn()")
    print("")

def clientLogIn(sck):

    user = sck.recv(1024).decode(FORMAT)
    print("username:--" + user +"--")

    sck.sendall(user.encode(FORMAT))
    
    pswd = sck.recv(1024).decode(FORMAT)
    print("password:--" + pswd +"--")
    
    accepted = check_clientLogIn(user, pswd)
    if accepted == 1:
        ID.append(user)
        account=str(Ad[Ad.__len__()-1])+"-"+str(ID[ID.__len__()-1])
        Live_Account.append(account)
    
    print("accept:", accepted)
    sck.sendall(str(accepted).encode(FORMAT))
    print("end-logIn()")
    print("")

def handle_Client(conn, addr):
    while True:

        option = conn.recv(1024).decode(FORMAT)

        if option == LOGIN:
            Ad.append(str(addr))
            clientLogIn(conn)        
        elif option == SIGNUP:
            clientSignUp(conn, addr)
        elif option == LOGOUT:
            Remove_LiveAccount(conn,addr)
        


    Remove_LiveAccount(conn,addr)
    conn.close()
    print("end-thread")


def runServer():
    try:
        print(HOST)
        print("Waiting for Client")

        while True:
            print("enter while loop")
            conn, addr = s.accept()


            clientThread = threading.Thread(target=handle_Client, args=(conn,addr))
            clientThread.daemon = True 
            clientThread.start()
        
            
            #handle_client(conn, addr)
            print("end main-loop")

        
    except KeyboardInterrupt:
        print("error")
        s.close()
    finally:
        s.close()
        print("end")

#-----------------------main-------------


sThread = threading.Thread(target=runServer)
sThread.daemon = True 
sThread.start()

input()

