import socket
import tkinter as tk 
from tkinter import *
from tkinter import messagebox
from tkinter import ttk 
from tkinter import filedialog as fd
import threading
from datetime import datetime
import os
from PIL import Image,ImageTk
import text_to_image

SEPARATOR="<SEPARATOR>"
HOST = "127.0.0.1"
PORT = 65432
HEADER = 64
FORMAT = "utf8"
DISCONNECT = "x"
USERNAME=""

LARGE_FONT = ("verdana", 13,"bold")
#option
SIGNUP = "signup"
LOGIN = "login"
LOGOUT = "logout"
SENDFILE="sendfile"
UPDATEFILE="updatefile"
RETRIEVEFILE="retrievefile"
DISPLAYFILE="displayfile"
class App(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.geometry("500x200")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.resizable(width=False, height=False)

        container = tk.Frame(self)
        container.pack(side="top", fill = "both", expand = True)
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (StartPage, HomePage):
            frame = F(container, self)

            self.frames[F] = frame 

            frame.grid(row=0, column=0, sticky="nsew")

        self.showFrame(StartPage)
    
    def showFrame(self, container):
        frame = self.frames[container]
        if container==HomePage:
            self.geometry("1000x1200")
        else:
            self.geometry("500x200")
        frame.tkraise()

    # close-programe function
    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()
            try:
                option = LOGOUT
                client.sendall(option.encode(FORMAT))
            except:
                pass

    def logIn(self,curFrame,sck):
        try:
            user = curFrame.entry_user.get()
            pswd = curFrame.entry_pswd.get()

            if user == "" or pswd == "":
                curFrame.label_notice = "Fields cannot be empty"
                return 
       
            #notice server for starting log in
            option = LOGIN
            sck.sendall(option.encode(FORMAT))

            #send username and password to server
            sck.sendall(user.encode(FORMAT))
            print("input:", user)

            sck.recv(1024)
            print("s responded")

            
            sck.sendall(pswd.encode(FORMAT))
            print("input:", pswd)


            # see if login is accepted
            accepted = sck.recv(1024).decode(FORMAT)
            print("accepted: "+ accepted)

            if accepted == "1":
                self.showFrame(HomePage)
                
                curFrame.label_notice["text"] = ""
            elif accepted == "2":
                curFrame.label_notice["text"] = "invalid username or password"
            elif  accepted == "0":
                curFrame.label_notice["text"] = "user already logged in"

        except:
            curFrame.label_notice["text"] = "Error: Server is not responding"
            print("Error: Server is not responding")

    def signUp(self,curFrame, sck):
        
        try:
        
            user = curFrame.entry_user.get()
            pswd = curFrame.entry_pswd.get()

            if pswd == "":
                curFrame.label_notice["text"] = "password cannot be empty"
                return 

            #notice server for starting log in
            option = SIGNUP
            sck.sendall(option.encode(FORMAT))
            
            
            #send username and password to server
            sck.sendall(user.encode(FORMAT))
            print("input:", user)

            sck.recv(1024)
            print("s responded")

            sck.sendall(pswd.encode(FORMAT))
            print("input:", pswd)


            # see if login is accepted
            accepted = sck.recv(1024).decode(FORMAT)
            print("accepted: "+ accepted)

            if accepted == "True":
                self.showFrame(HomePage)
                curFrame.label_notice["text"] = ""
            else:
                curFrame.label_notice["text"] = "username already exists"

        except:
            curFrame.label_notice["text"] = "Error 404: Server is not responding"
            print("404")

    def logout(self,curFrame, sck):
        try:
            option = LOGOUT
            sck.sendall(option.encode(FORMAT))
            accepted = sck.recv(1024).decode(FORMAT)
            if accepted == "True":
                self.showFrame(StartPage)
        except:
            curFrame.label_notice["text"] = "Error: Server is not responding"

    def sendFile(self,curFrame,sck):
        try:
            option=SENDFILE
            sck.sendall(option.encode(FORMAT))
            file_name=fd.askopenfilename()
            size=os.path.getsize(file_name)
            sck.sendall(file_name.encode(FORMAT))
            receive=sck.recv(1024).decode(FORMAT)
            sck.sendall(str(size).encode(FORMAT))
            receive=sck.recv(1024).decode(FORMAT)
            if receive=="1":
                with open(file_name,"rb") as f:
                    bytes_read=f.read(size)
                    sck.sendall(bytes_read)
            # with open(file_name,"rb") as f:
            #     while True:
            #         bytes_read=f.read(1024)
            #         if not bytes_read:
            #             sck.send(b'-+Done+-')
            #             receive=sck.recv(1024)
            #             if(receive==b'-+Success+-'):
            #                 break
            #         sck.sendall(bytes_read)
            username=self.frames[StartPage].entry_user.get()
            sck.send(username.encode(FORMAT))
            curFrame.label_notice["text"]="Send file successfully"
        except: 
            curFrame.label_notice["text"]="Error: Server is not responding"
    def updateFile(self,curFrame,file_variable,sck):
        try:
            option=UPDATEFILE
            sck.sendall(option.encode(FORMAT))
            user=self.frames[StartPage].entry_user.get()
            sck.sendall(user.encode(FORMAT))
            listFile=sck.recv(4096).decode(FORMAT)
            listFile=eval(listFile)
            option=curFrame.file_option["menu"]
            option.delete(0,"end")

            for string in listFile:
                option.add_command(label=string, 
                             command=lambda value=string:
                                    file_variable.set(value))
            curFrame.label_notice["text"]="Update file successfully"
        except: 
            curFrame.label_notice["text"]="Error: Server is not responding"
    def retrieveFile(self,curFrame,sck):
        try:
            option=RETRIEVEFILE
            sck.sendall(option.encode(FORMAT))
            nameFile=curFrame.file_variable.get()
            nameFile=nameFile[2:len(nameFile)-3]
            sck.sendall(nameFile.encode(FORMAT))
            receive=sck.recv(1024).decode(FORMAT)
            if receive=="1":
                username=self.frames[StartPage].entry_user.get()
                sck.sendall(username.encode(FORMAT))
            name=sck.recv(1024).decode(FORMAT)
            sck.send("1".encode(FORMAT))
            Type=sck.recv(1024).decode(FORMAT)
            sck.send("1".encode(FORMAT))
            size=int(sck.recv(1024).decode(FORMAT))
            sck.send("1".encode(FORMAT))
            content=sck.recv(size)
            with open(name+Type,"wb") as f:
                f.write(content)
            curFrame.label_notice["text"]="Retrive file successfully"
        except:
            curFrame.label_notice["text"]="Error: Server is not responding"
    
    def displayFile(self,curFrame,panel,sck):
        try:
            option=DISPLAYFILE
            sck.sendall(option.encode(FORMAT))
            nameFile=curFrame.file_variable.get()
            nameFile=nameFile[2:len(nameFile)-3]
            sck.sendall(nameFile.encode(FORMAT))
            receive=sck.recv(1024).decode(FORMAT)
            if receive=="1":
                username=self.frames[StartPage].entry_user.get()
                sck.sendall(username.encode(FORMAT))
            size=int(sck.recv(1024).decode(FORMAT))
            sck.send("1".encode(FORMAT))
            content=sck.recv(size)
            sck.send("1".encode(FORMAT))
            Type=sck.recv(1024).decode(FORMAT)
            curFrame.text.delete("1.0","end")
            with open(nameFile+Type,"wb") as f:
                f.write(content)
            if Type==".txt":
                text_file=open(nameFile+Type,"r")
                stuff=text_file.read()
                curFrame.text.insert(END,stuff)
                return
            elif Type==".png": path=nameFile+".png"
            elif Type==".jpg": path=nameFile+".jpg"
            original_img=Image.open(path)
            resize_img=original_img.resize((300,300))
            img=ImageTk.PhotoImage(resize_img)
            panel.configure(image=img)
            panel.image=img
            curFrame.label_notice["text"]="Display file successfully"
        except: 
            curFrame.label_notice["text"]="Error: Server is not responding"
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
    
        label_title = tk.Label(self, text="LOG IN", font=LARGE_FONT)
        label_user = tk.Label(self, text="username ",fg='#20639b',font='verdana 10 ')
        label_pswd = tk.Label(self, text="password ",fg='#20639b',font='verdana 10 ')

        self.label_notice = tk.Label(self,text="")
        self.entry_user = tk.Entry(self,width=20,bg='light yellow')
        self.entry_pswd = tk.Entry(self,width=20,bg='light yellow')

        button_log = tk.Button(self,text="LOG IN", bg="#20639b",fg='floral white',command=lambda: controller.logIn(self, client)) 
        button_log.configure(width=10)
        button_sign = tk.Button(self,text="SIGN UP",bg="#20639b",fg='floral white', command=lambda: controller.signUp(self, client)) 
        button_sign.configure(width=10)
        
        label_title.pack()
        label_user.pack()
        self.entry_user.pack()
        label_pswd.pack()
        self.entry_pswd.pack()
        self.label_notice.pack()

        button_log.pack()
        button_sign.pack()

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.listFile=['']
        self.path="white.jpg"
        label_title = tk.Label(self, text="HOME PAGE", font=LARGE_FONT,fg='#20639b')
        button_back = tk.Button(self, text="LOG OUT", command=lambda: controller.logout(self,client))
        send_back = tk.Button(self, text="SEND FILE",command=lambda:controller.sendFile(self,client))
        update_back= tk.Button(self, text="UPDATE FILE LIST",command=lambda: controller.updateFile(self,self.file_variable,client))
        retrieve_back= tk.Button(self, text="RETRIEVE FILE",command=lambda: controller.retrieveFile(self,client))
        display_back= tk.Button(self, text="DISPLAY FILE",command=lambda: controller.displayFile(self,self.panel,client))
        self.label_notice=tk.Label(self,text="",bg="light yellow")
        self.file_variable=tk.StringVar(self)
        self.file_variable.set("File list")
        self.file_option=tk.OptionMenu(self, self.file_variable,*self.listFile)
        original_img=Image.open(self.path)
        resize_img=original_img.resize((300,300))
        img=ImageTk.PhotoImage(resize_img)
        self.panel=tk.Label(self,image=img)
        self.panel.image=img
        self.text=Text(self,width=30,height=10,font=("Helvetica",16))
        label_title.pack(pady=10)
        button_back.pack(pady=2)
        send_back.pack(pady=2)
        self.file_option.pack()
        update_back.pack(pady=2)
        retrieve_back.pack(pady=2)
        display_back.pack(pady=2)
        self.panel.pack()
        self.text.pack()
        self.label_notice.pack()
    



# class FilePage(tk.Frame):
#     def __init__(self,parent,controller):
#         tk.Frame.__init__(self,parent)

#         lable_title=tk.Label(self,text="FILE PAGE",font=LARGE_FONT,fg='#20639b',bg="light yellow")
#         listFile=controller.retrieveFile(self,client)
#         file=tk.StringVar(listFile)
#         file.set("Select file to retrieve")
#         menu=tk.OptionMen(tk.Frame,file, *listFile)
#         menu.pack()
        
#--------------------------main------------------------

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (HOST, PORT)
client.connect(server_address)


app = App() 



#main
try:
    app.mainloop()
except:
    print("Error: server is not responding")
    client.close()

finally:
    client.close()
