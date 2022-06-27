import os
from datetime import datetime
from getpass import getpass
import mysql.connector
from mysql.connector import Error
from twilio.rest import Client
from tkinter import *
from tabulate import tabulate
from tkinter import messagebox
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
import numpy as np

def create_db(user_name, user_pass,host_name,db_name):
    try:
        mydb = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_pass,
        )
        mycursor = mydb.cursor()
        query_create_db = "CREATE DATABASE IF NOT EXISTS " + db_name
        mycursor.execute(query_create_db)
        print("\n***Database is successfully created***\n")
    except Error as e:
         messagebox.showerror('Error', f"\nERROR : {e} occurred !\n")

query_create_table_customers = '''CREATE TABLE IF NOT EXISTS customers(
    acc_num int AUTO_INCREMENT,
    f_name varchar(20) NOT NULL,
    l_name varchar(20) NOT NULL,
    aadhar_num varchar(20) NOT NULL,
    dob varchar(10) NOT NULL,
    city varchar(20) NOT NULL,
    area varchar(20) NOT NULL,
    pincode varchar(12) NOT NULL,
    phone_num varchar(12) NOT NULL,
    email_id varchar(30) NOT NULL,
    account_type varchar(10) NOT NULL,
    sms_banking varchar(2),
    current_amount float NOT NULL,
    PRIMARY KEY(acc_num)
);'''

query_create_table_transactions = '''
CREATE TABLE IF NOT EXISTS transactions(
    trans_id int AUTO_INCREMENT,
    acc_num int,
    amount float,
    type varchar(10),
    date varchar(20),
    PRIMARY KEY(trans_id),
    FOREIGN KEY (acc_num) REFERENCES customers(acc_num)
);'''

query_create_table_auth = '''
CREATE TABLE IF NOT EXISTS auth(
    acc_num int,
    password varchar(100) NOT NULL,
    FOREIGN KEY (acc_num) REFERENCES customers(acc_num)
);'''

admin_id = '0000'
admin_passwd = 'root'

def backmenu(frme):
    try:
        frme.destroy()
    except:
        pass
    main_menu_admin(connection)

def create_connection(user_name, user_pass, host_name,db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_pass,
            database=db_name
        )
        print("\n***Connection to MySQL database is successfull***\n")
    except Error as e:
         messagebox.showerror('Error', f"\nERROR : {e} occurred !\n")
    return connection

def execute_query(connection, query):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        return 1
    except Error as e:
         messagebox.showerror('Error', f"ERROR : {e} occurred !")
         return 0

def read_table(connection, table_name="", query=""):
    nxt = Tk()
    cursor = connection.cursor()
    result=None
    if query == "":
        read_table_query = "SELECT * FROM " + table_name
    else:
        read_table_query = query
    try:
        cursor.execute(read_table_query)
        result=cursor.fetchall()
        if table_name=="customers":
            nxt.geometry("1300x500")
            nxt.title("Account Details")
            mainmenu = Button(nxt, text = "Back" ,font='Verdana 10 bold',bg="gold", command = lambda:backmenu(nxt),height=2,width=12)
            mainmenu.place(x=950, y=440)
            column_names = [description[0] for description in cursor.description]
            t1=tabulate(result, headers=column_names, tablefmt='psql')
            Label(nxt,text=t1,font="consolas 8").pack()
        if table_name=="transactions":
            nxt.geometry("700x900")
            nxt.title("Account Details")
            mainmenu = Button(nxt, text = "Back" ,font='Verdana 10 bold',bg="gold", command = lambda:backmenu(nxt),height=2,width=12)
            mainmenu.place(x=550, y=50)
            column_names = [description[0] for description in cursor.description]
            t1=tabulate(result, headers=column_names, tablefmt='psql')
            Label(nxt,text=t1,font="consolas 10").place(x=0,y=0)
        nxt.mainloop()
    except Error as e:
        messagebox.showerror('Error', f"ERROR : {e} occurred !")

def authenticate(connection, acc, pw, level):
    if level == 'admin':
        account = int(acc)
        passwrd = pw
        
        if acc == admin_id and passwrd == admin_passwd:
            return True
    elif level == 'customer':
        usr_id = int(accountvalue1.get())
        pass_word = passwrdvalue1.get()
        p = getDetail(connection, "auth",("acc_num", usr_id, 'int'), "password")
        if pass_word == p:
            return True
    return False

def main_menu_admin(connection):
    auth = authenticate(connection, accountvalue.get(), passwrdvalue.get(), "admin")
    inter1.destroy()
    global admin
    admin = Tk()
    if auth == True:
        admin.geometry('800x500')  
        admin.title("B.M.S.")
        Label(admin, text="BANK MANAGEMENT SYSTEM",
            font="comicsansms 20 bold", pady=15).place(x=30,y=10)
        Label(admin, text="Select your option",
            font="comicsansms 16 bold", pady=15).place(x=60,y=80)
        global var1
        var1 = IntVar()
        R1 = Radiobutton(admin, text="Open new account",font="comicsansms 13 bold", variable=var1, value=1,
                    command=admin_actions)
        R1.place(x=100,y=150)

        R2 = Radiobutton(admin, text="Update existing Account     ",font="comicsansms 13 bold", variable=var1, value=2,
                    command=admin_actions)
        R2.place(x=100,y=200)

        R3 = Radiobutton(admin, text="Close existing Account      ",font="comicsansms 13 bold", variable=var1, value=3
                    ,command=admin_actions)
        R3.place(x=100,y=250)

        R4 = Radiobutton(admin, text="See all Customers details   ",font="comicsansms 13 bold", variable=var1, value=4,
                        command=admin_actions)
        R4.place(x=100,y=300)

        R5 = Radiobutton(admin, text="See all Transactions details",font="comicsansms 13 bold", variable=var1, value=5
                    ,command=admin_actions)
        R5.place(x=100,y=350)

        R6 = Radiobutton(admin, text="Exit",font="comicsansms 13 bold", variable=var1, value=6
                    ,command=admin_actions)
        R6.place(x=100,y=400)
        admin.mainloop()
    else:
         messagebox.showerror('Error', "Wrong credentials !")

def admin_actions():
    #admin.destroy()
    ch = var1.get()
    if ch == 1:
        add_new_account(connection)
    elif ch == 2:
        update_account(connection)
    elif ch == 3:
        close_account(connection)
    elif ch == 4:
        read_table(connection, "customers")
    elif ch == 5:
        read_table(connection, "transactions")
    elif ch == 6:
        exit()
    else:
         messagebox.showerror('Error', "Invalid Input !")

def main_menu_customer(connection, acc, pw):
    auth = authenticate(connection, acc, pw, "customer")
    if auth == True:
        transaction_menu(connection,acc)
    else:
        messagebox.showwarning("Warning","Invalid Credentials")

def add_new_account(connection):
    global f_name
    global l_name 
    global aadhar_num 
    global dob 
    global city , area ,pincode ,phone_num , email_id ,account_type ,sms_banking ,current_amount
    def switch():
        query_insert_new_account = '''INSERT INTO customers (f_name,l_name,aadhar_num,dob,city,area,
                pincode,phone_num,email_id,account_type,sms_banking,current_amount) VALUES (''' + \
                "'"+f_name.get()+"'" + "," + "'"+l_name.get()+"'" + "," + "'"+aadhar_num.get()+"'" + "," + \
                "'"+dob.get()+"'" + "," + "'"+city.get()+"'" + "," + "'"+area.get()+"'" + "," + "'"+pincode.get()+ \
                "'" + "," + "'"+phone_num.get()+"'" + "," + "'"+email_id.get()+"'" + "," + "'"+account_type.get()+"'" + \
                "," + "'"+sms_banking.get()+"'" + "," + current_amount.get() + ");"
        status1 = execute_query(connection, query_insert_new_account)
        acc_n = getDetail(connection, "customers",("aadhar_num", aadhar_num.get(), 'str'), "acc_num")
        query_insert_auth = "INSERT INTO auth (acc_num, password) VALUES (" + str(acc_n) + \
            "," + "'" + password.get() + "'" + ");"
        status2 = execute_query(connection, query_insert_auth)
        if status1 and status2 == 1:
                messagebox.showinfo("Successful","***Record inserted successfully...***")
                addAcc.destroy()

    def clear():
        f_name.delete(0,END)
        l_name.delete(0,END)
        aadhar_num.delete(0,END)
        dob.delete(0,END)
        city.delete(0,END)
        area.delete(0,END)
        pincode.delete(0,END)
        phone_num.delete(0,END)
        email_id.delete(0,END)
        account_type.delete(0,END)
        sms_banking.delete(0,END)
        current_amount.delete(0,END)
        password.delete(0,END)
    
    addAcc = Tk()
    addAcc.title("Bank Management System")
    addAcc.maxsize(width=700 ,  height=600)
    addAcc.minsize(width=700 ,  height=600)
    heading = Label(addAcc , text = "Add New Account" , font = 'Verdana 20 bold')
    heading.place(x=60 , y=40)
    f_name = Label(addAcc, text= "First Name :" , font='Verdana 10 bold')
    f_name.place(x=120,y=100)
    l_name = Label(addAcc, text= "Last Name :" , font='Verdana 10 bold')
    l_name.place(x=120,y=130)
    aadhar_num = Label(addAcc, text= "Aadhar Number :" , font='Verdana 10 bold')
    aadhar_num.place(x=120,y=160)
    dob = Label(addAcc, text= "Date Of Birth :" , font='Verdana 10 bold')
    dob.place(x=120,y=190)
    city = Label(addAcc, text= "City :" , font='Verdana 10 bold')
    city.place(x=120,y=220)
    area = Label(addAcc, text= "Area :" , font='Verdana 10 bold')
    area.place(x=120,y=250)
    pincode = Label(addAcc, text= "Pincode :" , font='Verdana 10 bold')
    pincode.place(x=120,y=280)
    phone_num = Label(addAcc, text= "Phone Number :" , font='Verdana 10 bold')
    phone_num.place(x=120,y=310)
    email_id = Label(addAcc, text= "Email Id :" , font='Verdana 10 bold')
    email_id.place(x=120,y=340)
    account_type = Label(addAcc, text= "Account Type :" , font='Verdana 10 bold')
    account_type.place(x=120,y=370)
    sms_banking = Label(addAcc, text= "Activate SMS service :" , font='Verdana 10 bold')
    sms_banking.place(x=120,y=400)
    current_amount = Label(addAcc, text= "Current Amount:" , font='Verdana 10 bold')
    current_amount.place(x=120,y=430)
    password = Label(addAcc, text= "Password :" , font='Verdana 10 bold')
    password.place(x=120,y=460)
   
    f_name = StringVar()
    l_name = StringVar()
    aadhar_num = StringVar()
    dob = StringVar()
    city= StringVar()
    area= StringVar()
    pincode = StringVar()
    phone_num = StringVar()
    email_id = StringVar()
    account_type = StringVar()
    sms_banking = StringVar()
    current_amount = StringVar()
    password = StringVar()
    f_name = Entry(addAcc, width=40 , textvariable = f_name)
    f_name.place(x=320 , y=100)
    l_name = Entry(addAcc, width=40 , textvariable = l_name)
    l_name.place(x=320 , y=130)
    aadhar_num = Entry(addAcc, width=40 , textvariable = aadhar_num)
    aadhar_num.place(x=320 , y=160)
    dob = Entry(addAcc, width=40, textvariable=dob)
    dob.place(x=320 , y=190)
    city = Entry(addAcc, width=40,textvariable = city)
    city.place(x=320 , y=220)
    area = Entry(addAcc, width=40 , textvariable = area)
    area.place(x=320 , y=250)
    pincode = Entry(addAcc, width=40 , textvariable = pincode)
    pincode.place(x=320 , y=280)
    phone_num = Entry(addAcc, width=40 , textvariable = phone_num)
    phone_num.place(x=320 , y=310)
    email_id = Entry(addAcc, width=40 , textvariable = email_id)
    email_id.place(x=320 , y=340)
    account_type = Entry(addAcc, width=40 , textvariable = account_type)
    account_type.place(x=320 , y=370)
    sms_banking = Entry(addAcc, width=40 , textvariable = sms_banking)
    sms_banking.place(x=320 , y=400)
    current_amount= Entry(addAcc, width=40  , textvariable = current_amount)
    current_amount.place(x=320 , y=430)
    password = Entry(addAcc, width=40, show="*", textvariable = password)
    password.place(x=320 , y=460)
    btn_signup = Button(addAcc, text = "Signup" ,font='Verdana 10 bold',bg="yellow", command = switch)
    btn_signup.place(x=400, y=513)
    btn_login = Button(addAcc, text = "Clear" ,font='Verdana 10 bold' ,bg="DeepSkyBlue2", command = clear)
    btn_login.place(x=480, y=513)
    mainmenu = Button(addAcc, text = "Back" ,font='Verdana 10 bold',bg="gold", command = lambda:backmenu(addAcc),height=2,width=12)
    mainmenu.place(x=460, y=40)
    addAcc.mainloop()

def updte():
    def upd1():
        if place == 'password':
            query_update_existing_account = "UPDATE auth SET " + place + " = " + \
          "'"  +new_data.get() +"'"   + " WHERE  acc_num = " + acc_num.get() + ';'
        else:        
            query_update_existing_account = "UPDATE customers SET " + place + " = " + \
         "'"  + new_data.get() + "'"  + " WHERE  acc_num = " + acc_num.get() + ';'
        status = execute_query(connection, query_update_existing_account)
        if status == 1:
            sms = getDetail(connection, "customers",
                            ("acc_num", acc_num.get(), 'int'), "sms_banking")
            if sms == 'Y':
                try:
                    sendSMS(connection, acc_num.get(), " updated " + " for "+place,0)
                except:
                    messagebox.showerror("Error","Kindly check your internet connection or mobile number !")
            messagebox.showinfo("Succrssful","***Record updated successfully...***") 
        updateAcc.destroy()
        nxt1.destroy()
        
    if not choica.get():
        messagebox.showwarning("Warning","Invalid Input !")
    else:
        global nxt1,place,new_data
        nxt1 = Tk()
        nxt1.geometry("600x250")
        nxt1.maxsize(600, 250)
        nxt1.minsize(600, 250)
        nxt1.title("Update Account Details")
        heading = Label(nxt1 , text = "Account Update " , font = 'Verdana 20 bold')
        heading.place(x=60 , y=40)
        ch=choica.get()
        
        if ch == '1':
            place = 'f_name'
            f_name = Label(nxt1, text= "First Name " , font='Verdana 10 bold')
            f_name.place(x=50,y=100)
            f_name = StringVar()
            f_name = Entry(nxt1, width=40 , textvariable = f_name)
            f_name.place(x=150 , y=100)
            new_data = f_name
        elif ch == '2':
            place = 'l_name'
            l_name = Label(nxt1, text= "Last Name " , font='Verdana 10 bold')
            l_name.place(x=50,y=100)
            l_name = StringVar()
            l_name = Entry(nxt1, width=40 , textvariable = l_name)
            l_name.place(x=150 , y=100)
            new_data = l_name
        elif ch == '3':
            place = "aadhar_num"
            aadhar_num = Label(nxt1, text= "Aadhar Number " , font='Verdana 10 bold')
            aadhar_num.place(x=50,y=100)
            aadhar_num = StringVar()
            aadhar_num = Entry(nxt1, width=40 , textvariable = aadhar_num)
            aadhar_num.place(x=250 , y=100)
            new_data = aadhar_num
        elif ch == '4':
            place = 'dob'
            dob = Label(nxt1, text= "Date Of Birth(DD/MM/YYYY) " , font='Verdana 10 bold')
            dob.place(x=50,y=100)
            dob = StringVar()
            dob = Entry(nxt1, width=40, textvariable=dob)
            dob.place(x=300 , y=100)
            new_data = dob
        elif ch == '5':
            place = 'city'
            city = Label(nxt1, text= "City " , font='Verdana 10 bold')
            city.place(x=50,y=100)
            city= StringVar()
            city = Entry(nxt1, width=40,textvariable = city)
            city.place(x=150 , y=100)
            new_data = city
        elif ch == '6':
            place = 'area'
            area = Label(nxt1, text= "Area " , font='Verdana 10 bold')
            area.place(x=50,y=100)
            area= StringVar()
            area = Entry(nxt1, width=40 , textvariable = area)
            area.place(x=150 , y=100)
            new_data = area
        elif ch == '7':
            place = 'pincode'
            pincode = Label(nxt1, text= "Pincode " , font='Verdana 10 bold')
            pincode.place(x=50,y=100)
            pincode = StringVar()
            pincode = Entry(nxt1, width=40 , textvariable = pincode)
            pincode.place(x=200 , y=100)
            new_data = pincode
        elif ch == '8':
            place = 'phone_num'
            phone = Label(nxt1, text= "Phone Number " , font='Verdana 10 bold')
            phone.place(x=50,y=100)
            phone = StringVar()
            phone = Entry(nxt1, width=40 , textvariable = phone)
            phone.place(x=200 , y=100)
            new_data = phone
        elif ch == '9':
            place = 'email_id'
            email = Label(nxt1, text= "Email Id " , font='Verdana 10 bold')
            email.place(x=50,y=100)
            email = StringVar()
            email = Entry(nxt1, width=40 , textvariable = email)
            email.place(x=200 , y=100)
            new_data = email
        elif ch == '10':
            place = 'account_type'
            account_type = Label(nxt1, text= "Account Type " , font='Verdana 10 bold')
            account_type.place(x=50,y=100)
            account_type = StringVar()
            account_type = Entry(nxt1, width=40 , textvariable = account_type)
            account_type.place(x=200 , y=100)
            new_data = account_type
        elif ch == '11':
            place = 'sms_banking'
            sms = Label(nxt1, text= "Activate SMS service " , font='Verdana 10 bold')
            sms.place(x=50,y=100)
            sms = StringVar()
            sms = Entry(nxt1, width=40 , textvariable = sms)
            sms.place(x=250 , y=100)
            new_data = sms
        elif ch == '12':
            place = 'password'
            password = Label(nxt1, text= "Password " , font='Verdana 10 bold')
            password.place(x=50,y=100)
            password = StringVar()
            password = Entry(nxt1, width=40, textvariable = password)
            password.place(x=200 , y=100)
            new_data =password
        else:
            messagebox.showwarning("Warning","Invalid Input !")
        btn_signup = Button(nxt1, text = "Update" ,font='Verdana 10 bold',bg="yellow", command = upd1)
        btn_signup.place(x=400, y=200)
        nxt1.mainloop()
        
def update_account(connection):
    global updateAcc
    updateAcc = Tk()
    global choica, acc_num
    choica = StringVar()
    acc_num = StringVar()
    updateAcc.title("Bank Management System")
    updateAcc.maxsize(width=700 ,  height=600)
    updateAcc.minsize(width=700 ,  height=600)
    heading = Label(updateAcc , text = "Update Account Details" , font = 'Verdana 20 bold')
    heading.place(x=60 , y=40)
    acc_num = Label(updateAcc, text= "Account Number :" , font='Verdana 10 bold')
    acc_num.place(x=120,y=100)
    acc_num = Entry(updateAcc, width=40 , textvariable = acc_num)
    acc_num.place(x=320 , y=100)
    choica = Label(updateAcc, text= "Select your choice :" , font='Verdana 10 bold')
    choica.place(x=120,y=150)
    choica = Entry(updateAcc, width=40 , textvariable = choica)
    choica.place(x=320 , y=150)
    f_name = Label(updateAcc, text= "1. First Name " , font='Verdana 10 bold')
    f_name.place(x=250,y=200)
    l_name = Label(updateAcc, text= "2. Last Name " , font='Verdana 10 bold')
    l_name.place(x=250,y=220)
    aadhar_num = Label(updateAcc, text= "3. Aadhar Number " , font='Verdana 10 bold')
    aadhar_num.place(x=250,y=240)
    dob = Label(updateAcc, text= "4. Date Of Birth " , font='Verdana 10 bold')
    dob.place(x=250,y=260)
    city = Label(updateAcc, text= "5. City " , font='Verdana 10 bold')
    city.place(x=250,y=280)
    area = Label(updateAcc, text= "6. Area " , font='Verdana 10 bold')
    area.place(x=250,y=300)
    pincode = Label(updateAcc, text= "7. Pincode " , font='Verdana 10 bold')
    pincode.place(x=250,y=320)
    phone = Label(updateAcc, text= "8. Phone Number " , font='Verdana 10 bold')
    phone.place(x=250,y=340)
    email = Label(updateAcc, text= "9. Email Id " , font='Verdana 10 bold')
    email.place(x=250,y=360)
    account_type = Label(updateAcc, text= "10. Account Type " , font='Verdana 10 bold')
    account_type.place(x=250,y=380)
    sms = Label(updateAcc, text= "11. Activate SMS service " , font='Verdana 10 bold')
    sms.place(x=250,y=400)
    password = Label(updateAcc, text= "12. Password " , font='Verdana 10 bold')
    password.place(x=250,y=420)
    btn_login = Button(updateAcc, text = "Submit" ,bg="yellow",font='Verdana 10 bold' , command = updte)
    btn_login.place(x=480, y=513)
    updateAcc.mainloop()

def close_account(connection):
    def dele():
        execute_query(connection,"SET FOREIGN_KEY_CHECKS=0;")
        query_close_account = "DELETE FROM customers WHERE acc_num = " + \
            str(acc_num.get()) + ';'
        status = execute_query(connection, query_close_account)
        query_close_account1 = "DELETE FROM auth WHERE acc_num = " + \
            str(acc_num.get()) + ';'
        status1 = execute_query(connection, query_close_account1)
        if status and status1 == 1:
            messagebox.showinfo("Successful","***Record deleted successfully...***")
        execute_query(connection,"SET FOREIGN_KEY_CHECKS=1;")
        nxt2.destroy()   
    global nxt2
    nxt2 = Tk()
    nxt2.geometry("600x250")
    nxt2.maxsize(600, 250)
    nxt2.minsize(600, 250)
    nxt2.title("Update Account Details")
    heading = Label(nxt2 , text = "Account Delete " , font = 'Verdana 20 bold')
    heading.place(x=60 , y=40)
    acc_num = Label(nxt2, text= "Account Number " , font='Verdana 10 bold')
    acc_num.place(x=50,y=100)
    acc_num = StringVar()
    acc_num = Entry(nxt2, width=40 , textvariable = acc_num)
    acc_num.place(x=200 , y=100)
    btn_login = Button(nxt2, text = "Submit" ,font='Verdana 10 bold' ,bg="yellow", command = dele)
    btn_login.place(x=400, y=200)
    mainmenu = Button(nxt2, text = "Back" ,font='Verdana 10 bold',bg="gold", command = lambda:backmenu(nxt2),height=2,width=12)
    mainmenu.place(x=460, y=40)
    nxt2.mainloop()
    
def sendSMS(connection, acc_num, cat, amount=0):
    account_sid = 'AC2150c8ff83f85f470552ac52276eb699'
    auth_token = '0f17614cb8ca100b97418ddd004384e8'
    to_num = '+91'+getDetail(connection, "customers",
                       ("acc_num", acc_num, 'int'), "phone_num")
    client = Client(account_sid, auth_token)
    f_name = getDetail(connection, "customers",
                       ("acc_num", acc_num, 'int'), "f_name")
    l_name = getDetail(connection, "customers",
                       ("acc_num", acc_num, 'int'), "l_name")
    message = client.messages.create(
        from_='+12566125541',
        body='Dear ' + str(f_name) + " " + str(l_name) + ', your account number ' +
        str(acc_num) + " is " + str(cat) + str(amount) + ".",
        to= to_num
    )

def doesAccountExist(connection, acc_num):
    query = 'SELECT * FROM customers WHERE acc_num = ' + str(acc_num) + ';'
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        records = cursor.fetchall()
        n = len(records)
        if(n <= 0):
            return 0
        else:
            return 1
    except Error as e:
         messagebox.showerror('Error', f"ERROR : {e} occurred !")

def getDetail(connection, table_name, cond, detail): 
    if cond[2] == 'str':
        query = 'SELECT ' + detail + ' FROM ' + table_name + ' WHERE ' + \
            str(cond[0]) + '=' + "'" + str(cond[1]) + "'" + ';'
    elif cond[2] == 'int':
        query = 'SELECT ' + detail + ' FROM ' + table_name + \
            ' WHERE ' + str(cond[0]) + '=' + str(cond[1]) + ';'
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        data = cursor.fetchall()
        data = data[0][0]
    except Error as e:
        messagebox.showerror('Error', f"ERROR : {e} occurred !")
    return data

def deposit_money(connection, acc_num):
    def dep():
        today = datetime.now()
        query_deposit_money = "UPDATE customers SET current_amount =   current_amount + " + \
            str(amount.get()) + " WHERE acc_num = " + str(acc_num) + ";"
        query_insert_transactions = "INSERT INTO transactions(acc_num,amount,type,date) VALUES ( " + \
            str(acc_num) + "," + str(amount.get()) + "," + "'" + "Credited" + "'" + "," "'" + \
            str(today)[:19] + "'" + ");"
        status = execute_query(connection, query_deposit_money) and execute_query(connection,
                                                                query_insert_transactions)
        if status == 1:
            sms = getDetail(connection, "customers",
                        ("acc_num", acc_num, 'int'), "sms_banking")
            if sms == 'Y':
                try:
                    sendSMS(connection, acc_num, " credited with ", amount.get())
                except:
                    messagebox.showerror("Error","Kindly check your internet connection or mobile number!")
            messagebox.showinfo("successful","***Amount deposited successfully...***")
        nxt3.destroy()

    global nxt3,amount
    nxt3 = Tk()
    nxt3.geometry("600x250")
    nxt3.maxsize(600, 250)
    nxt3.minsize(600, 250)
    nxt3.title("Transaction")
    heading = Label(nxt3 , text = "Deposit Money " , font = 'Verdana 20 bold')
    heading.place(x=60 , y=40)
    amo = Label(nxt3, text= "Amount " , font='Verdana 10 bold')
    amo.place(x=50,y=100)
    amount = IntVar()
    amount = Entry(nxt3, width=40 , textvariable = amount)
    amount.place(x=200 , y=100)
    btn_login = Button(nxt3, text = "Submit" ,font='Verdana 10 bold' ,bg="yellow", command = dep)
    btn_login.place(x=400, y=200)
    nxt3.mainloop()

def withdraw_money(connection, acc_num):
    def wthdrw():
        amount = float(amountw.get())
        curr_amnt = getDetail(connection, "customers",
                          ("acc_num", acc_num, 'int'), "current_amount")
        if amount > curr_amnt:
            messagebox.showinfo("You don't have sufficient balance!")
        else:
            today = datetime.now()
            query_withdraw_money = "UPDATE customers SET current_amount  =   current_amount - " + \
                str(amount) + " WHERE acc_num = " + str(acc_num) + ";"
            query_insert_transactions = "INSERT INTO transactions(acc_num,amount,type,date) VALUES ( " + \
                str(acc_num) + "," + str(amount) + "," + "'" + "Debited" + "'" + "," + "'" + \
                str(today)[:19] + "'" + ");"
            status = execute_query(connection, query_withdraw_money) and execute_query(connection,
                                                                        query_insert_transactions)
            if status == 1:
                sms = getDetail(connection, "customers",
                                ("acc_num", acc_num, 'int'), "sms_banking")
                if sms == 'Y':
                    try:
                        sendSMS(connection, acc_num, " debited by ", amount)
                    except:
                        messagebox.showerror("Error","Kindly check your internet connection or mobile number!")
                messagebox.showinfo("successful","***Amount withdrawn successfully...***")
            nxt4.destroy()
    global nxt4,amountw
    nxt4 = Tk()
    nxt4.geometry("600x250")
    nxt4.maxsize(600, 250)
    nxt4.minsize(600, 250)
    nxt4.title("Transaction")
    heading = Label(nxt4 , text = "Withdraw Money " , font = 'Verdana 20 bold')
    heading.place(x=60 , y=40)
    amo = Label(nxt4, text= "Amount " , font='Verdana 10 bold')
    amo.place(x=50,y=100)
    amountw = IntVar()
    amountw = Entry(nxt4, width=40 , textvariable = amountw)
    amountw.place(x=200 , y=100)
    btn_login = Button(nxt4, text = "Submit" ,font='Verdana 10 bold' ,bg="yellow", command = wthdrw)
    btn_login.place(x=400, y=200)
    nxt4.mainloop()

def display_graph1(connection,acc_num):
    mycursor = connection.cursor()
    query1='SELECT * FROM transactions WHERE acc_num = '+ str(acc_num) +';'
    mycursor.execute(query1)
    result = mycursor.fetchall
    amnt=[]
    tran=[]
    c=0
    for i in mycursor:
        amnt.append(i[2])
        c=c+1
        tran.append(c)
    x = np.array(tran)
    y = np.array(amnt)
    X_Y_Spline = make_interp_spline(x, y)
    X_ = np.linspace(x.min(), x.max(), 50)
    Y_ = X_Y_Spline(X_)
    cust.destroy()
    plt.plot(X_, Y_)
    plt.title("Amount in bank")
    plt.xlabel(" Number of Transactions")
    plt.ylabel("Balance")
    plt.show()

def transaction_menu(connection,acc):
    os.system('cls' if os.name == 'nt' else 'clear')
    inter2.destroy()
    global cust
    cust = Tk()
    cust.title("Banking-Management-System")
    cust.geometry('500x600')
    cust.maxsize(500, 600)
    cust.minsize(500, 600)
    img = PhotoImage(file='C:/Users/Shoaib/Python/BMS/bk1.png')
    img1 = img.subsample(4, 4)
    Label(cust, image=img1).place(height=100, width=100, x=0.3, y=0.05)
    
    Label(cust, text="Select your option",
            font="comicsansms 20 bold", pady=15).place(x=120,y=30)

    Button(text="  Deposit  ", command=lambda:cust_choice1(connection),font="comicsansms 10 bold" ,bg="deep sky blue",width=20,height=3).place(x=100,y=100)
    Button(text="  Withdraw  ", command=lambda:cust_choice2(connection),font="comicsansms 10 bold" ,bg="green2",width=20,height=3).place(x=260,y=200)
    Button(text="  Balance  ", command=lambda:cust_choice3(connection),font="comicsansms 10 bold" ,bg="gold",width=20,height=3).place(x=100,y=300)
    Button(text="  Status  ", command=lambda:display_graph(connection),font="comicsansms 10 bold" ,bg="orange",width=20,height=3).place(x=260,y=400)
    Button(text="  Exit  ", command=lambda:exit(),font="comicsansms 10 bold" ,bg="red",width=20,height=3).place(x=100,y=500)
    def cust_choice1(connection):
        acc_num = accountvalue1.get()
        if doesAccountExist(connection, acc_num) == 1:
            deposit_money(connection, acc_num)
        else:
             messagebox.showerror('Error', "Account doesn't exists !")

    def cust_choice2(connection):    
        acc_num = accountvalue1.get()
        if doesAccountExist(connection, acc_num) == 1:
                withdraw_money(connection, acc_num)
        else:
            messagebox.showerror('Error', "Account doesn't exists !")
    def cust_choice3(connection):
        acc_num = accountvalue1.get()
        messagebox.showinfo("Balance","Your current balance is : ₹" + str(getDetail(connection,
                  "customers", ("acc_num", acc_num, 'int'), "current_amount")))

    def display_graph(connection):
        acc_num = accountvalue1.get()
        if doesAccountExist(connection, acc_num) == 1:
            display_graph1(connection, acc_num)
        else:
            messagebox.showerror('Error', "Account doesn't exists !")
        
    
def admin_creds():
    main_menu_admin(connection)

def customer_creds(acc_num,passwd):
    main_menu_customer(connection, acc_num, passwd)

def admin_ac():
    root.destroy()
    global inter1
    inter1 = Tk()
    global accountvalue
    global passwrdvalue
    img = PhotoImage(file='C:/Users/Shoaib/Python/BMS/admin.png')
    img1 = img.subsample(3, 3)
    Label(inter1, image=img1).place(height=150, width=150, x=0.3, y=0.05)
    accountvalue = StringVar()
    passwrdvalue = StringVar()
    inter1.geometry("800x400")
    inter1.maxsize(800,400)
    inter1.minsize(800,400)
    inter1.title("B.M.S")
    Label(inter1, text="Admin Login",
          font="comicsansms 20 bold", pady=15).place(x=150, y=50)
    account_id = Label(inter1, text="Account id",font="comicsansms 15")
    password = Label(inter1, text="Password",font="comicsansms 15")
    account_id.place(x=200, y=160)
    password.place(x=200, y=220)
    accountentry = Entry(inter1, textvariable=accountvalue)
    passwrdentry = Entry(inter1, textvariable=passwrdvalue, show='*')

    accountentry.place(x=350, y=160)
    passwrdentry.place(x=350, y=220)

    Button(text="Submit", command=lambda:admin_creds(), height = 2, width = 13,font="comicsansms 10",bg="yellow").place(x=500, y=300)
    inter1.mainloop()

def customer_ac():
    root.destroy()
    global inter2
    
    inter2 = Tk()
    global accountvalue1
    global passwrdvalue1
    img = PhotoImage(file='C:/Users/Shoaib/Python/BMS/clogin.png')
    img1 = img.subsample(4, 4)
    Label(inter2, image=img1).place(height=150, width=150, x=0.3, y=0.05)

    accountvalue1 = StringVar()
    passwrdvalue1 = StringVar()
    inter2.geometry("800x400")
    inter2.maxsize(800, 400)
    inter2.minsize(800, 400)
    inter2.title("B.M.S")
    Label(inter2, text="Customer Login",
          font="comicsansms 20 bold", pady=15).place(x=150, y=50)
    account_id1 = Label(inter2, text="Account id",font="comicsansms 15")
    password1 = Label(inter2, text="Password",font="comicsansms 15")
    account_id1.place(x=200, y=160)
    password1.place(x=200, y=220)

    accountentry1 = Entry(inter2, textvariable=accountvalue1)
    passwrdentry1= Entry(inter2, textvariable=passwrdvalue1, show='*')

    accountentry1.place(x=350, y=160)
    passwrdentry1.place(x=350, y=220)

    Button(text="Submit", command=lambda:customer_creds(account_id1, password1), height = 2, width = 13,font="comicsansms 10",bg="yellow").place(x=500, y=300)
    inter2.mainloop()

def sel():
        choice  = var.get()
        if choice == 1:
            admin_ac()
        elif choice == 2:
            customer_ac()
        else:
            messagebox.showerror("Error","Invalid Input !")

if __name__ == "__main__":
    host_name = 'localhost'
    user_name = 'root'
    user_pass = '7075036042Shoaib'
    db_name = 'bank'
    create_db(user_name,user_pass,host_name,db_name)
    connection = create_connection(user_name,user_pass,host_name,db_name)
    execute_query(connection, query_create_table_customers) and execute_query(connection, 
             query_create_table_transactions) and execute_query(connection, query_create_table_auth)
    root = Tk()
    root.geometry("800x800")
    bg = PhotoImage(file = "C:/Users/Shoaib/Python/BMS/bank.png")
    label1 = Label( root, image = bg, bg='white')
    label1.place(x = 0, y = 0, relwidth=1, relheight = 1)
    root.maxsize(800, 800)
    root.minsize(800, 800)
    root.title("B.M.S.")
    Label(root, text="BANK MANAGEMENT SYSTEM",
          font="comicsansms 20 bold",bg='white', pady=15).place(x=200,y=0)
    Label(root, text="  Login Panel  ",
          font="comicsansms 15 bold",bg="SteelBLue1", pady=15).place(x=330,y=370)
    var = IntVar()
    R1 = Radiobutton(root, text="Admin  ",font="comicsansms 13",bg="SteelBLue2", variable=var, value=1,
                  command=sel)
    R1.place(x=368,y=450)
    R2 = Radiobutton(root, text="Customer",font="comicsansms 13",bg="SteelBLue2", variable=var, value=2,
                  command=sel)
    R2.place(x=368,y=500)
    root.mainloop()
    