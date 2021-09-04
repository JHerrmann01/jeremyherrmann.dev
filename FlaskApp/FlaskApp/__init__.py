from flask import Flask, request, jsonify, render_template, make_response, redirect, url_for
from flask_api import status
from InstagramAPI import InstagramAPI
from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import urllib
import urllib2
import time
import threading
import sqlite3
import random
import os

app = Flask(__name__)

################################################################################################
###############STARTING HERE, THESE ENDPOINTS ARE RELATED TO MY PERSONAL WEBPAGE!###############
################################################################################################

@app.route("/updated/", methods=["GET"])
def homepageUpdated():
    try:
        return(render_template('updatedIndex.html'))
    except Exception as e:
        return(str(e))




courses = (
    ("CSE 214",["CSE214", "Computer Science II"],),
    ("CSE 215",["CSE215", "Foundations of Computer Science"],),
    ("CSE 219",["CSE219", "Computer Science III"],),
    ("CSE 220",["CSE220", "System Fundamentals I"],),
    ("CSE 300",["CSE300", "Tecnical Communications"],),
    ("CSE 303",["CSE303", "Theory of Computation"],),
    ("CSE 305",["CSE305", "Principles of Database Systems"],),
    ("CSE 307",["CSE307", "Principles of Programming Languages"],),
    ("CSE 310",["CSE310", "Computer Networks"],),
    ("CSE 320",["CSE320", "System Fundamentals II"],),
    ("CSE 352",["CSE352", "Artificial Intelligence"],),
    ("CSE 385",["CSE385", "Analysis of Algorithms: Honors"],),
)

@app.route("/", methods=["GET"])
def homepage():
    try:
        return(render_template('index.html',courses=courses))
    except Exception as e:
        return(str(e))

@app.route("/portfolio/", methods=["GET"])
def portfolio():
    try:
        return(render_template('portfolio.html'))
    except Exception as e:
        return(str(e))

@app.route("/courses/<requested_course>/", methods=["GET"])
def coursesEndpoint(requested_course):
    try:
        requested_course = requested_course.upper()
        for course in courses:
            if(course[1][0] == requested_course):
                return(render_template('courses/' + requested_course + '.html', course=course))
        return("Sorry! I actually haven't taken that course yet! Try again next semester :)")
    except Exception as e:
        return(str(e))
        return("Sorry! At this time I haven't written anything about this course! Check again in a few days :)")

@app.route("/resume/", methods=["GET"])
def resume():
    return app.send_static_file('Jeremy_Herrmann_Resume.pdf')

@app.route("/courses/<requested_course>/<requested_document>/", methods=["GET"])
def course_documents(requested_course, requested_document):
    try:
        requested_course = requested_course.upper()
        if(requested_course == "CSE219"):
            requested_document = requested_document.upper()
            if(requested_document == "SDD"):
                return app.send_static_file('Documents/' + requested_course + '/SDD.pdf')
        elif(requested_course == "CSE300"):
            requested_document = requested_document.upper()
            if(requested_document == "PRESSRELEASE"):
                return app.send_static_file('Documents/' + requested_course + '/News_Release.pdf')
            elif(requested_document == "USERINSTRUCTION"):
                return app.send_static_file('Documents/' + requested_course + '/User_Instructions.pdf')
            elif(requested_document == "AUDIENCEAWARENESS"):
                return app.send_static_file('Documents/' + requested_course + '/Audience_Awareness.pdf')
            elif(requested_document == "COLLABORATIVEPROJECT"):
                return app.send_static_file('Documents/' + requested_course + '/Fix_Solar.pdf')
            elif(requested_document == "VISUALCOMMUNICATION"):
                return app.send_static_file('Documents/' + requested_course + '/Visual_Communication.pdf')
        return redirect(url_for('homepage'))
    except Exception as e:
        return(str(e))


################################################################################################
###############STARTING HERE, THESE ENDPOINTS ARE RELATED TO THE CSE 305 PROJECT!###############
################################################################################################

#Below is the location of the database on the server
CSE305_DATABASE = '/var/www/FlaskApp/FlaskApp/eBoy.db'

#Below are some functions which are used to query/post into the database.
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
# Query will be used to get information from the database #
def query_db_target(query, database, args=(), dictionary = True):
    con = sqlite3.connect(database)
    if dictionary:
        con.row_factory = dict_factory
    cur = con.cursor()
    cur.execute(query, args)
    rv = cur.fetchall()
    con.commit()
    con.close()
    return rv

# Post will be used to change/input information into the database #
def post_db_target(query, database, args=()):
    con = sqlite3.connect(database)
    cur = con.cursor()
    cur.execute(query, args)
    con.commit()
    con.close()

def begin_transaction(database):
    con = sqlite3.connect(database)
    con.row_factory = dict_factory
    cur = con.cursor()
    return con, cur

from flask import session
from datetime import datetime, timedelta

@app.route("/CSE305/", methods=["GET"])
def CSE305_eBoyHomepage():
    try:
        #Checking if the current person is already logged in as a User
        if('UserID' in session):
            #Checking to see if the user exists in the DB -- If so, we should grab the users information
            current_user = None
            try:
                values = (session['UserID'],)
                current_user = query_db_target("SELECT * FROM User WHERE UserID=?", CSE305_DATABASE, values)
                #If there are no users with this userid, we should redirect and clear the session
                if(len(current_user) == 0):
                    session.clear()
                    return redirect(url_for('CSE305_eBoyHomepage'))
            except Exception as query_exception:
                return(str(query_exception))

            #At this point, we have all the user's information and we know they exist!

            #Checking if we are looking for a certain category / searching for a specific item
            item_name = None
            type = None
            if("search_query" in request.args):
                item_name = request.args.get("search_query")
            if("type" in request.args):
                type = request.args.get("type")

            #Grabbing all the current items available for listing!
            all_items = []
            try:
                if(item_name != None and type != None):
                    values = (type, '%'+ item_name + '%',)
                    all_items = query_db_target("SELECT Inventory.`ItemID`, `Name`, `Description`, `Price`, `TypeName` FROM Inventory LEFT JOIN Item ON Inventory.ItemID=Item.ItemID LEFT JOIN HasType ON Item.ItemID=HasType.ItemID LEFT JOIN Type ON HasType.TypeID=Type.TypeID WHERE Inventory.Quantity>0 AND Type.TypeID=? AND Item.Name LIKE ?;", CSE305_DATABASE, values)
                elif(item_name != None):
                    values = ('%'+ item_name + '%',)
                    all_items = query_db_target("SELECT Inventory.`ItemID`, `Name`, `Description`, `Price` FROM Inventory LEFT JOIN Item ON Inventory.ItemID=Item.ItemID WHERE Inventory.Quantity>0 AND Item.Name LIKE ?;", CSE305_DATABASE, values)
                elif(type != None):
                    values = (type,)
                    all_items = query_db_target("SELECT Inventory.`ItemID`, `Name`, `Description`, `Price`, `TypeName` FROM Inventory LEFT JOIN Item ON Inventory.ItemID=Item.ItemID LEFT JOIN HasType ON Item.ItemID=HasType.ItemID LEFT JOIN Type ON HasType.TypeID=Type.TypeID WHERE Inventory.Quantity>0 AND Type.TypeID=?;", CSE305_DATABASE, values)
                else:
                    all_items = query_db_target("SELECT * FROM Inventory LEFT JOIN Item ON Inventory.ItemID=Item.ItemID WHERE Inventory.Quantity > 0;", CSE305_DATABASE)
                if(len(all_items) == 0):
                    all_items = []
            except Exception as query_exception:
                return(str(query_exception))

            popular_items = []
            try:
                popular_items = query_db_target("SELECT Orders.ItemID, Item.Name, Item.Description, Item.Price, COUNT(Orders.OrderID) FROM Orders LEFT JOIN Inventory ON Orders.ItemID = Inventory.ItemID LEFT JOIN Item ON Inventory.ItemID = Item.ItemID WHERE Inventory.Quantity > 0 GROUP BY Orders.ItemID ORDER BY COUNT(Orders.OrderID) DESC, Orders.ItemID ASC LIMIT 3;", CSE305_DATABASE)
                if(len(popular_items) == 0):
                    popular_items = []
            except Exception as query_exception:
                return(str(query_exception))

            #Grabbing the list of categories
            categories = []
            try:
                categories = query_db_target("SELECT `TypeID`, `TypeName` FROM Type", CSE305_DATABASE)
            except Exception as query_exception:
                return(str(query_exception))
            return(render_template('CSE305/MainPage.html', UserID=str(session['UserID']), Categories=categories, Items=all_items, Popular_Items=popular_items))
        else:
            return(render_template('CSE305/LandingPage.html'))
    except Exception as e:
        return(str(e))

@app.route("/CSE305/employee/", methods=["GET"])
def CSE305_eBoyEmployeeHomepage():
    try:
        #Checking if the current person is already logged in as an employee
        if('EmployeeID' in session):
            #Checking to see if the user exists in the DB -- If so, we should grab the users information
            current_employee = None
            try:
                values = (session['EmployeeID'],)
                current_employee = query_db_target("SELECT E.EmployeeID, E.RoleID, E.Username, R.RoleName, R.Rank, E.ManagerID, M.Username as ManagerUsername FROM Employee E LEFT JOIN Role R ON E.RoleID=R.RoleID LEFT JOIN Employee M ON E.ManagerID=M.EmployeeID WHERE E.EmployeeID=?;", CSE305_DATABASE, values)
                #If there are no users with this userid, we should redirect and clear the session
                if(len(current_employee) == 0):
                    session.clear()
                    return redirect(url_for('CSE305_eBoyEmployeeHomepage'))
            except Exception as query_exception:
                return(str(query_exception))

            #At this point, we have all the user's information and we know they exist!
            permissions = None
            subordinates = None
            allRanksUnder = None
            try:
                #Getting the permissions for the user
                values = (current_employee[0]['RoleID'],)
                permissions = query_db_target("SELECT HasPermission.PermissionID, PermissionDescription, PermissionShort FROM HasPermission LEFT JOIN Permissions ON HasPermission.PermissionID=Permissions.PermissionID WHERE HasPermission.RoleID=?;", CSE305_DATABASE, values)
                #Getting the permissions for the user
                values = (current_employee[0]['EmployeeID'],)
                subordinates = query_db_target("SELECT * FROM Employee E WHERE E.ManagerID=?;", CSE305_DATABASE, values)
                #Getting all the ranks under the current employee's rank
                values = (current_employee[0]['Rank'], )
                allRanksUnder = query_db_target("SELECT * FROM Role R WHERE R.Rank < ?;", CSE305_DATABASE, values)
            except Exception as query_exception:
                return(str(query_exception))

            can_add_employee = False # Done
            can_remove_review = False
            can_remove_posting = False
            can_change_permissions = False # Done
            can_view_user = False
            can_remove_employee = False
            can_edit_inventory = False
            for permission in permissions:
                if(permission['PermissionDescription'] == "Add Employee"):
                    can_add_employee = True
                if(permission['PermissionDescription'] == "Remove Review"):
                    can_remove_review = True
                if(permission['PermissionDescription'] == "Remove Posting"):
                    can_remove_posting = True
                if(permission['PermissionDescription'] == "Change Permissions"):
                    can_change_permissions = True
                if(permission['PermissionDescription'] == "View User"):
                    can_view_user = True
                if(permission['PermissionDescription'] == "Remove Employee"):
                    can_remove_employee = True
                if(permission['PermissionDescription'] == "Edit Inventory"):
                    can_edit_inventory = True

            allSellers = query_db_target("SELECT DISTINCT Post.UserID, User.Username FROM Inventory LEFT JOIN Post ON Inventory.ItemID=Post.ItemID LEFT JOIN User ON User.UserID=Post.UserID;", CSE305_DATABASE)

            return(render_template('CSE305/EmployeeHomePage.html', Employee=current_employee[0], Permissions=permissions, Subordinates=subordinates, AllRanks=allRanksUnder, AllSellers=allSellers,
            CanAddEmployee=can_add_employee, CanRemoveReview=can_remove_review, CanRemovePosting=can_remove_posting, CanChangePermissions=can_change_permissions, CanViewUser=can_view_user, CanRemoveEmployee=can_remove_employee, CanEditInventory=can_edit_inventory))
        else:
            return(render_template('CSE305/EmployeeLandingPage.html'))
    except Exception as e:
        return(str(e))

@app.route("/CSE305/employee_inventory_view/", methods=["GET"])
def CSE305_employeeInventoryView():
    try:
        #Checking if the current person is already logged in as an employee
        if('EmployeeID' in session):
            #Checking to see if the user exists in the DB -- If so, we should grab the users information
            current_employee = None
            try:
                values = (session['EmployeeID'],)
                current_employee = query_db_target("SELECT E.EmployeeID, E.RoleID, E.Username, R.RoleName, R.Rank, E.ManagerID, M.Username as ManagerUsername FROM Employee E LEFT JOIN Role R ON E.RoleID=R.RoleID LEFT JOIN Employee M ON E.ManagerID=M.EmployeeID WHERE E.EmployeeID=?;", CSE305_DATABASE, values)
                #If there are no users with this userid, we should redirect and clear the session
                if(len(current_employee) == 0):
                    session.clear()
                    return redirect(url_for('CSE305_eBoyEmployeeHomepage'))
            except Exception as query_exception:
                return(str(query_exception))

            permissions = None
            try:
                #Getting the permissions for the user
                values = (current_employee[0]['RoleID'],)
                permissions = query_db_target("SELECT HasPermission.PermissionID, PermissionDescription, PermissionShort FROM HasPermission LEFT JOIN Permissions ON HasPermission.PermissionID=Permissions.PermissionID WHERE HasPermission.RoleID=?;", CSE305_DATABASE, values)
            except Exception as query_exception:
                return(str(query_exception))

            can_edit_inventory = False
            for permission in permissions:
                if(permission['PermissionDescription'] == "Edit Inventory"):
                    can_edit_inventory = True

            if(not can_edit_inventory):
                return redirect(url_for('CSE305_eBoyEmployeeHomepage'))

            #Grabbing all the current items available for listing!
            all_items = []
            try:
                all_items = query_db_target("SELECT * FROM Inventory LEFT JOIN Item ON Inventory.ItemID=Item.ItemID WHERE Inventory.Quantity > 0;", CSE305_DATABASE)
                if(len(all_items) == 0):
                    all_items = []
            except Exception as query_exception:
                return(str(query_exception))

            can_remove_posting = False
            for permission in permissions:
                if(permission['PermissionDescription'] == "Remove Posting"):
                    can_remove_posting = True

            return(render_template('CSE305/EmployeeInventoryDisplay.html', Employee=current_employee[0], Items=all_items, CanRemovePosting=can_remove_posting,))
        else:
            return(render_template('CSE305/EmployeeLandingPage.html'))
    except Exception as e:
        return(str(e))

@app.route("/CSE305/register/", methods=["POST"])
def CSE305_register():
    try:
        firstname = str(request.form["register_firstname"])
        lastname = str(request.form["register_lastname"])
        email = str(request.form["register_email"])
        password = str(request.form["register_password"])
        username = str(request.form["register_username"])

        #Attempting to INSERT the new User, if this post request fails, then we will be directed into the exception below!
        try:
            values = (username, firstname, lastname, email, password,)
            query = post_db_target("INSERT INTO User(Username, FirstName, Lastname, Email, Password) VALUES (?, ?, ?, ?, ?)", CSE305_DATABASE, values)
        except Exception as query_exception:
            return("Sorry, the email address or username you attempted to use is already active!" + str(query_exception))

        #Attempting to LOGIN the new User
        try:
            values = (username,)
            query = query_db_target("SELECT `UserID` FROM User WHERE Username=?", CSE305_DATABASE, values)
            #If the new User was successfully created, we will log the user in!
            session['UserID'] = str(query[0]['UserID'])
            return("Success")
        except Exception as query_exception:
            return("There was an error attempting to log you in!" + str(query_exception))
        return(str(query))
    except Exception as e:
        return("Failure - " +str(e))

@app.route("/CSE305/login/", methods=["POST"])
def CSE305_login():
    try:
        username = str(request.form["login_username"])
        password = str(request.form["login_password"])

        #Attempting to LOGIN the new User
        try:
            values = (username,)
            query = query_db_target("SELECT *, COUNT(*) FROM User WHERE Username=?", CSE305_DATABASE, values)

            #If there are any Users with this Username, we will select them and compare their password the password we received.
            if(int(query[0]['COUNT(*)']) == 1):
                if(str(query[0]['Password']) == password):
                    session['UserID'] = str(query[0]['UserID'])
                    return("Success")
                else:
                    return("Invalid Password!")
            else:
                return("No user associated with this Username!")
        except Exception as query_exception:
            return("Sorry, this account doesn't exist!" + str(query_exception))
    except Exception as e:
        return(str(e))

@app.route("/CSE305/employee_login/", methods=["POST"])
def CSE305_EmployeeLogin():
    try:
        username = str(request.form["login_username"])
        password = str(request.form["login_password"])

        #Attempting to LOGIN the new User
        try:
            values = (username,)
            query = query_db_target("SELECT *, COUNT(*) FROM Employee WHERE Username=?", CSE305_DATABASE, values)

            #If there are any Users with this Username, we will select them and compare their password the password we received.
            if(int(query[0]['COUNT(*)']) == 1):
                if(str(query[0]['Password']) == password):
                    session['EmployeeID'] = str(query[0]['EmployeeID'])
                    return("Success")
                else:
                    return("Invalid Password!")
            else:
                return("No EmployeeID associated with this Username!")
        except Exception as query_exception:
            return("Sorry, this account doesn't exist!" + str(query_exception))
    except Exception as e:
        return(str(e))

@app.route("/CSE305/logout/", methods=["POST"])
def CSE305_logout():
    try:
        session.clear()
        return("Success")
    except Exception as e:
        return(str(e))

@app.route("/CSE305/viewUser/", methods=["GET"])
def CSE305_View_User():
    try:
        #Checking if the current person is already logged in as an employee
        if('EmployeeID' in session):
            #Checking to see if the user exists in the DB -- If so, we should grab the users information
            current_employee = None
            try:
                values = (session['EmployeeID'],)
                current_employee = query_db_target("SELECT E.EmployeeID, E.RoleID, E.Username, R.RoleName, R.Rank, E.ManagerID, M.Username as ManagerUsername FROM Employee E LEFT JOIN Role R ON E.RoleID=R.RoleID LEFT JOIN Employee M ON E.ManagerID=M.EmployeeID WHERE E.EmployeeID=?;", CSE305_DATABASE, values)
                #If there are no users with this userid, we should redirect and clear the session
                if(len(current_employee) == 0):
                    session.clear()
                    return redirect(url_for('CSE305_eBoyEmployeeHomepage'))
            except Exception as query_exception:
                return(str(query_exception))

            #Checking to see if the user exists in the DB -- If so, we should grab the users information

            #Grabbing the specific item we are looking for
            Username = None
            if("Username" in request.args):
                Username = request.args.get("Username")
            else:
                return redirect(url_for('CSE305_eBoyEmployeeHomepage'))

            current_user = None
            try:
                values = (Username,)
                current_user = query_db_target("SELECT * FROM User WHERE Username=?", CSE305_DATABASE, values)
                #If there are no users with this userid, we should redirect and clear the session
                if(len(current_user) == 0):
                    return redirect(url_for('CSE305_eBoyEmployeeHomepage'))
            except Exception as query_exception:
                return(str(query_exception))

            #At this point, we have all the user's information and we know they exist!
            permissions = None
            try:
                #Getting the permissions for the user
                values = (current_employee[0]['RoleID'],)
                permissions = query_db_target("SELECT HasPermission.PermissionID, PermissionDescription, PermissionShort FROM HasPermission LEFT JOIN Permissions ON HasPermission.PermissionID=Permissions.PermissionID WHERE HasPermission.RoleID=?;", CSE305_DATABASE, values)
            except Exception as query_exception:
                return(str(query_exception))

            can_view_user = False
            can_remove_user = False
            for permission in permissions:
                if(permission['PermissionDescription'] == "Remove User"):
                    can_remove_user = True
                if(permission['PermissionDescription'] == "View User"):
                    can_view_user = True

            if(can_view_user == False):
                return redirect(url_for('CSE305_eBoyEmployeeHomepage'))

            return(render_template('CSE305/View_User.html', User=current_user[0], Employee=current_employee[0], CanRemoveUser=can_remove_user,))
        else:
            return(render_template('CSE305/EmployeeLandingPage.html'))
    except Exception as e:
        return(str(e))

@app.route("/CSE305/profile/", methods=["GET"])
def CSE305_profile():
    try:
        #If the user is not logged in, redirect the user to the homepage!
        if('UserID' not in session):
            return redirect(url_for('CSE305_eBoyHomepage'))

        #Checking to see if the user exists in the DB -- If so, we should grab the users information
        current_user = None
        try:
            values = (session['UserID'],)
            current_user = query_db_target("SELECT * FROM User WHERE UserID=?", CSE305_DATABASE, values)
            #If there are no users with this userid, we should redirect and clear the session
            if(len(current_user) == 0):
                session.clear()
                return redirect(url_for('CSE305_eBoyHomepage'))
        except Exception as query_exception:
            return(str(query_exception))

        #At this point, we have all the user's information and we know they exist!

        #Grabbing the User's Payment Info
        payment_information = None
        try:
            values = (session['UserID'],)
            payment_information = query_db_target("SELECT `CardNum`, `Expiration`, `CVC` FROM Payment WHERE `UserID`=?", CSE305_DATABASE, values)
            if(len(payment_information) == 0):
                payment_information = None
            else:
                payment_information = payment_information[0]
        except Exception as query_exception:
            return(str(query_exception))

        #Grabbing all the user's orders
        orders = []
        try:
            values = (session['UserID'],)
            orders = query_db_target("SELECT DISTINCT `OrderID`, `OrderDateTime` FROM Orders WHERE `UserID`=?", CSE305_DATABASE, values)
            if(len(orders) == 0):
                orders = None
        except Exception as query_exception:
            return(str(query_exception))

        #Grabbing all current items a user is selling
        current_items = []
        try:
            values = (session['UserID'],)
            current_items = query_db_target("SELECT * FROM Post LEFT JOIN Inventory ON Post.ItemID=Inventory.ItemID LEFT JOIN Item ON Item.ItemID=Post.ItemID WHERE `UserID`=? AND Inventory.Quantity > 0", CSE305_DATABASE, values)

            if(len(current_items) == 0):
                current_items = None
        except Exception as query_exception:
            return(str(query_exception))

        #Grabbing all the item categories
        categories = []
        try:
            categories = query_db_target("SELECT `TypeID`, `TypeName` FROM Type", CSE305_DATABASE)
        except Exception as query_exception:
            return(str(query_exception))

        #Otherwise, Display the profile page!
        return(render_template('CSE305/Profile.html', User=current_user[0], Categories=categories, PaymentInfo=payment_information, Orders=orders, CurrentListing=current_items))
    except Exception as e:
        return(str(e))

@app.route("/CSE305/viewOrder/", methods=["GET"])
def CSE305_viewOrder():
    try:
        #If the user is not logged in, redirect the user to the homepage!
        if('UserID' not in session):
            return redirect(url_for('CSE305_eBoyHomepage'))

        #Checking to see if the user exists in the DB -- If so, we should grab the users information
        current_user = None
        try:
            values = (session['UserID'],)
            current_user = query_db_target("SELECT * FROM User WHERE UserID=?", CSE305_DATABASE, values)
            #If there are no users with this userid, we should redirect and clear the session
            if(len(current_user) == 0):
                session.clear()
                return redirect(url_for('CSE305_eBoyHomepage'))
        except Exception as query_exception:
            return(str(query_exception))

        #At this point, we have all the user's information and we know they exist!

        order = request.args.get("OrderID")
        #Grabbing all the user's orders
        orders = []
        try:
            values = (order,)
            orders = query_db_target("SELECT * FROM Orders LEFT JOIN Item ON Orders.ItemID=Item.ItemID WHERE `OrderID`=?", CSE305_DATABASE, values)
            if(len(orders) == 0):
                orders = None
        except Exception as query_exception:
            return(str(query_exception))

        #Grabbing all the item categories
        categories = []
        try:
            categories = query_db_target("SELECT `TypeID`, `TypeName` FROM Type", CSE305_DATABASE)
        except Exception as query_exception:
            return(str(query_exception))

        #Otherwise, Display the profile page!
        return(render_template('CSE305/ViewOrder.html', User=current_user, Order=orders, Categories=categories))
    except Exception as e:
        return(str(e))

@app.route("/CSE305/cart/", methods=["GET"])
def CSE305_shopping_cart():
    #Checking if the current person is already logged in as a User
    if('UserID' in session):
        #Checking to see if the user exists in the DB -- If so, we should grab the users information
        current_user = None
        try:
            values = (session['UserID'],)
            current_user = query_db_target("SELECT * FROM User WHERE UserID=?", CSE305_DATABASE, values)
            #If there are no users with this userid, we should redirect and clear the session
            if(len(current_user) == 0):
                session.clear()
                return redirect(url_for('CSE305_eBoyHomepage'))
        except Exception as query_exception:
            return(str(query_exception))

        #At this point, we have all the user's information and we know they exist!

        #Grabbing the information regarding the user's items
        all_items = []
        try:
            values = (session['UserID'],)
            all_items = query_db_target("SELECT Item.Name, Item.Price, ShoppingCart.Quantity, (PRICE*QUANTITY) FROM ShoppingCart LEFT JOIN Item ON Item.ItemID=ShoppingCart.ItemID WHERE UserID=?;", CSE305_DATABASE, values)
        except Exception as query_exception:
            return(str(query_exception))

        #Grabbing the User's Payment Info
        payment_information = None
        try:
            values = (session['UserID'],)
            payment_information = query_db_target("SELECT `CardNum`, `Expiration`, `CVC` FROM Payment WHERE `UserID`=?", CSE305_DATABASE, values)
            if(len(payment_information) == 0):
                payment_information = None
            else:
                payment_information = payment_information[0]
        except Exception as query_exception:
            return(str(query_exception))

        #Grabbing the list of categories
        categories = []
        try:
            categories = query_db_target("SELECT `TypeID`, `TypeName` FROM Type", CSE305_DATABASE)
        except Exception as query_exception:
            return(str(query_exception))
        return(render_template('CSE305/ShoppingCart.html', AllItems=all_items, PaymentInfo=payment_information))
    else:
        return(render_template('CSE305/LandingPage.html'))

@app.route("/CSE305/postItem/", methods=["GET"])
def CSE305_post_item():
    try:
        #If the user is not logged in, redirect the user to the homepage!
        if('UserID' not in session):
            return redirect(url_for('CSE305_eBoyHomepage'))

        #Checking to see if the user exists in the DB -- If so, we should grab the users information
        current_user = None
        try:
            values = (session['UserID'],)
            current_user = query_db_target("SELECT * FROM User WHERE UserID=?", CSE305_DATABASE, values)
            #If there are no users with this userid, we should redirect and clear the session
            if(len(current_user) == 0):
                session.clear()
                return redirect(url_for('CSE305_eBoyHomepage'))
        except Exception as query_exception:
            return(str(query_exception))

        #At this point, we have all the user's information and we know they exist!

        #Grabbing all the item categories
        categories = []
        try:
            categories = query_db_target("SELECT `TypeID`, `TypeName` FROM Type", CSE305_DATABASE)
        except Exception as query_exception:
            return(str(query_exception))

        return(render_template('CSE305/PostItem.html', Categories=categories))
    except Exception as e:
        return(str(e))

@app.route("/CSE305/upload_item/", methods=["POST"])
def CSE305_upload_item():
    try:
        #If the user is not logged in, redirect the user to the homepage!
        if('UserID' not in session):
            return redirect(url_for('CSE305_eBoyHomepage'))

        #Checking to see if the user exists in the DB -- If so, we should grab the users information
        current_user = None
        try:
            values = (session['UserID'],)
            current_user = query_db_target("SELECT * FROM User WHERE UserID=?", CSE305_DATABASE, values)
            #If there are no users with this userid, we should redirect and clear the session
            if(len(current_user) == 0):
                session.clear()
                return redirect(url_for('CSE305_eBoyHomepage'))
        except Exception as query_exception:
            return(str(query_exception))

        #At this point, we have all the user's information and we know they exist!

        #Creating the connection & cursor
        con, cur = begin_transaction(CSE305_DATABASE)

        #Beginning the transaction!
        try:
            cur.execute("BEGIN TRANSACTION", ())
            #Inserting into the Item Relation
            values = (request.form['itemPrice'], request.form['itemDesc'], request.form['itemName'])
            cur.execute("INSERT INTO Item(Price, Description, Name) VALUES (?, ?, ?)", values)
            #Checking if the rowcount is less than or equal to 0
            if(cur.rowcount <= 0):
                con.rollback()
                con.close()
                return("Fail to insert into Item")

            #Grabbing the ItemID of the Row we just inserted
            cur.execute("SELECT `ItemID` FROM Item WHERE rowid=?", (cur.lastrowid,))
            ItemID = cur.fetchone()
            ItemID = ItemID['ItemID']

            #Inserting all the HasType entries
            #Traversing the arguments
            for argument in request.form:
                #If the current argument starts with "Category" check the result of the argument
                if( str(argument).startswith("CATEGORY-") ):
                    #Check the corresponding value
                    if(str(request.form[argument]) == "true"):
                        #Grabbing the TypeID
                        TypeID = int(str(argument).split("CATEGORY-")[1])
                        #Setting up values to be inserted
                        values = (ItemID, TypeID,)
                        cur.execute("INSERT INTO HasType(ItemID, TypeID) VALUES (?, ?)", values)
                        #Checking the result of the insertion
                        if(cur.rowcount <= 0):
                            con.rollback()
                            con.close()
                            return("Fail to insert the Type for the Item")

            #Inserting into the Post Relation
            values = (session['UserID'], ItemID, request.form['itemQuantity'], datetime.now())
            cur.execute("INSERT INTO Post(UserID, ItemID, Quantity, PostDateTime) VALUES (?, ?, ?, ?)", values)
            #Checking if the rowcount is less than or equal to 0
            if(cur.rowcount <= 0):
                con.rollback()
                con.close()
                return("Fail to insert into Post")

            #Inserting into the Inventory Relation
            values = (ItemID, request.form['itemQuantity'],)
            cur.execute("INSERT INTO Inventory(ItemID, Quantity) VALUES (?, ?)", values)
            #Checking if the rowcount is less than or equal to 0
            if(cur.rowcount <= 0):
                con.rollback()
                con.close()
                return("Fail to insert into Inventory")

            con.commit()
        except Exception as query_exception:
            con.rollback()
            return(str(query_exception))
        con.close()
        return(str(request.form))
    except Exception as e:
        return(str(e))

@app.route("/CSE305/item/", methods=["GET"])
def CSE305_display_item():
    try:
        #Checking if the current person is already logged in as a User
        if('UserID' in session or 'EmployeeID' in session):
            #Checking to see if the user exists in the DB -- If so, we should grab the users information
            current_user = None
            #Checking to see if the user exists in the DB -- If so, we should grab the users information
            current_employee = None
            if('UserID' in session):
                try:
                    values = (session['UserID'],)
                    current_user = query_db_target("SELECT * FROM User WHERE UserID=?", CSE305_DATABASE, values)
                    #If there are no users with this userid, we should redirect and clear the session
                    if(len(current_user) == 0):
                        session.clear()
                        return redirect(url_for('CSE305_eBoyHomepage'))
                except Exception as query_exception:
                    return(str(query_exception))
            elif('EmployeeID' in session):
                try:
                    values = (session['EmployeeID'],)
                    current_employee = query_db_target("SELECT E.EmployeeID, E.RoleID, E.Username, R.RoleName, R.Rank, E.ManagerID, M.Username as ManagerUsername FROM Employee E LEFT JOIN Role R ON E.RoleID=R.RoleID LEFT JOIN Employee M ON E.ManagerID=M.EmployeeID WHERE E.EmployeeID=?;", CSE305_DATABASE, values)
                    #If there are no users with this userid, we should redirect and clear the session
                    if(len(current_employee) == 0):
                        session.clear()
                        return redirect(url_for('CSE305_eBoyEmployeeHomepage'))
                except Exception as query_exception:
                    return(str(query_exception))

            #At this point, we have all the user's information and we know they exist!

            #Grabbing the specific item we are looking for
            itemID = None
            if("itemID" in request.args):
                itemID = request.args.get("itemID")
            else:
                if(current_employee == None):
                    return redirect(url_for('CSE305_eBoyHomepage'))
                else:
                    return redirect(url_for('CSE305_eBoyEmployeeHomepage'))

            #Grabbing the information regarding the item we are querying
            item = []
            try:
                values = (itemID,)
                item = query_db_target("SELECT Item.ItemID, Item.Name, Item.Description, Item.Price, Inventory.Quantity, GROUP_CONCAT(Type.TypeName) FROM Inventory LEFT JOIN Item ON Inventory.ItemID=Item.ItemID LEFT JOIN HasType ON Item.ItemID=HasType.ItemID LEFT JOIN Type ON HasType.TypeID=Type.TypeID WHERE Inventory.ItemID = ? GROUP BY Item.ItemID, Item.Name, Item.Description, Item.Price, Inventory.Quantity;", CSE305_DATABASE, values)
            except Exception as query_exception:
                return(str(query_exception))

            if(len(item) == 0):
                return redirect(url_for('CSE305_eBoyHomepage'))
            else:
                item = item[0]

            reviews = []
            try:
                values = (itemID,)
                reviews = query_db_target("SELECT Review.ReviewID, Review.ReviewDateTime, Review.Description, Review.Rating, User.Username FROM Review LEFT JOIN User ON Review.UserID=User.UserID WHERE Review.ItemID = ?;", CSE305_DATABASE, values)
            except Exception as query_exception:
                return(str(query_exception))

            if('UserID' in session):
                #Grabbing the list of categories
                categories = []
                try:
                    categories = query_db_target("SELECT `TypeID`, `TypeName` FROM Type", CSE305_DATABASE)
                except Exception as query_exception:
                    return(str(query_exception))
                return(render_template('CSE305/ItemPage.html', UserID=str(session['UserID']), Categories=categories, CurrentItem=item, Reviews=reviews))
            else:
                #At this point, we have all the user's information and we know they exist!
                permissions = None
                try:
                    #Getting the permissions for the user
                    values = (current_employee[0]['RoleID'],)
                    permissions = query_db_target("SELECT HasPermission.PermissionID, PermissionDescription, PermissionShort FROM HasPermission LEFT JOIN Permissions ON HasPermission.PermissionID=Permissions.PermissionID WHERE HasPermission.RoleID=?;", CSE305_DATABASE, values)
                except Exception as query_exception:
                    return(str(query_exception))

                can_remove_review = False
                can_edit_inventory = False
                for permission in permissions:
                    if(permission['PermissionDescription'] == "Remove Review"):
                        can_remove_review = True
                    if(permission['PermissionDescription'] == "Edit Inventory"):
                        can_edit_inventory = True
                return(render_template('CSE305/ItemPageEmployee.html', Employee=current_employee, CurrentItem=item, Reviews=reviews, CanRemoveReview=can_remove_review, CanEditInventory=can_edit_inventory))
        else:
            return(render_template('CSE305/LandingPage.html'))
    except Exception as e:
        return(str(e))

@app.route("/CSE305/add_employee/", methods=["POST"])
def CSE305_Add_Employee():
    try:
        #Checking if the current person is already logged in as an employee
        if('EmployeeID' in session):
            #Checking to see if the user exists in the DB -- If so, we should grab the users information
            current_employee = None
            try:
                values = (session['EmployeeID'],)
                current_employee = query_db_target("SELECT E.EmployeeID, E.RoleID, E.Username, R.RoleName, R.Rank, E.ManagerID, M.Username as ManagerUsername FROM Employee E LEFT JOIN Role R ON E.RoleID=R.RoleID LEFT JOIN Employee M ON E.ManagerID=M.EmployeeID WHERE E.EmployeeID=?;", CSE305_DATABASE, values)
                #If there are no users with this userid, we should redirect and clear the session
                if(len(current_employee) == 0):
                    session.clear()
                    return redirect(url_for('CSE305_eBoyEmployeeHomepage'))
            except Exception as query_exception:
                return(str(query_exception))

            #Getting the arguments
            employeeUsername = str(request.form["employeeUsername"])
            employeePassword = str(request.form["employeePassword"])
            rank = str(request.form["employeeRank"])

            #Attempting to INSERT the new Review, if this post request fails, then we will be directed into the exception below!
            try:
                values = (int(rank), employeePassword, datetime.now(), session['EmployeeID'], employeeUsername,)
                query = post_db_target("INSERT INTO Employee(RoleID, Password, StartDate, EndDate, ManagerID, Username) VALUES (?, ?, ?, null, ?, ?)", CSE305_DATABASE, values)
            except Exception as query_exception:
                return("we failed to insert into employee!" + str(query_exception))
            return("success")
        else:
            return(render_template('CSE305/EmployeeLandingPage.html'))
    except Exception as e:
        return(str(e))

@app.route("/CSE305/submit_review/", methods=["POST"])
def CSE305_submit_review():
    try:
        #Checking if the current person is already logged in as a User
        if('UserID' in session):
            #Checking to see if the user exists in the DB -- If so, we should grab the users information
            current_user = None
            try:
                values = (session['UserID'],)
                current_user = query_db_target("SELECT * FROM User WHERE UserID=?", CSE305_DATABASE, values)
                #If there are no users with this userid, we should redirect and clear the session
                if(len(current_user) == 0):
                    session.clear()
                    return redirect(url_for('CSE305_eBoyHomepage'))
            except Exception as query_exception:
                return(str(query_exception))

            #Getting the arguments
            itemID = str(request.form["itemID"])
            reviewContent = str(request.form["reviewContent"])
            rating = str(request.form["rating"])

            #Attempting to INSERT the new Review, if this post request fails, then we will be directed into the exception below!
            try:
                values = (datetime.now(), session['UserID'], itemID, reviewContent, rating,)
                query = post_db_target("INSERT INTO Review(ReviewDateTime, UserID, ItemID, Description, Rating) VALUES (?, ?, ?, ?, ?)", CSE305_DATABASE, values)
            except Exception as query_exception:
                return("We failed to create the review!" + str(query_exception))

            #At this point, we have all the user's information and we know they exist!
            return("success")
        else:
            return("Failure - User is not logged in with a valid account!")
    except Exception as e:
        return("Failure" + str(e))

@app.route("/CSE305/add_to_cart/", methods=["POST"])
def CSE305_add_to_cart():
    try:
        #Checking if the current person is already logged in as a User
        if('UserID' in session):
            #Checking to see if the user exists in the DB -- If so, we should grab the users information
            current_user = None
            try:
                values = (session['UserID'],)
                current_user = query_db_target("SELECT * FROM User WHERE UserID=?", CSE305_DATABASE, values)
                #If there are no users with this userid, we should redirect and clear the session
                if(len(current_user) == 0):
                    session.clear()
                    return redirect(url_for('CSE305_eBoyHomepage'))
            except Exception as query_exception:
                return(str(query_exception))

            #Getting the arguments
            itemID = str(request.form["itemID"])

            #Attempting to INSERT the new Review, if this post request fails, then we will be directed into the exception below!
            try:
                values = (session['UserID'], itemID,)
                query = post_db_target("INSERT OR IGNORE INTO ShoppingCart(UserID, ItemID, Quantity) VALUES (?, ?, 0);", CSE305_DATABASE, values)
                query = post_db_target("UPDATE ShoppingCart SET Quantity = Quantity + 1 WHERE UserID=? AND ItemID=?;", CSE305_DATABASE, values)
            except Exception as query_exception:
                return("Unable to add the item to your shopping cart!" + str(query_exception))

            #At this point, we have all the user's information and we know they exist!
            return("success")
        else:
            return("Failure - User is not logged in with a valid account!")
    except Exception as e:
        return("Failure" + str(e))

@app.route("/CSE305/update_payment/", methods=["POST"])
def CSE305_update_payment():
    try:
        #Checking if the current person is already logged in as a User
        if('UserID' in session):
            #Checking to see if the user exists in the DB -- If so, we should grab the users information
            current_user = None
            try:
                values = (session['UserID'],)
                current_user = query_db_target("SELECT * FROM User WHERE UserID=?", CSE305_DATABASE, values)
                #If there are no users with this userid, we should redirect and clear the session
                if(len(current_user) == 0):
                    session.clear()
                    return redirect(url_for('CSE305_eBoyHomepage'))
            except Exception as query_exception:
                return(str(query_exception))

            #Getting the arguments
            cardNum = str(request.form["cardNum"])
            expiration = str(request.form["expiration"])
            cvc = str(request.form["cvc"])

            try:
                values = (cardNum, expiration, cvc, session['UserID'])
                query = post_db_target("UPDATE Payment SET CardNum=?, Expiration=?, CVC=? WHERE UserID=?;", CSE305_DATABASE, values)
            except Exception as query_exception:
                return("Unable to update the payment method!" + str(query_exception))

            #At this point, we have all the user's information and we know they exist!
            return("success")
        else:
            return("Failure - User is not logged in with a valid account!")
    except Exception as e:
        return("Failure" + str(e))

@app.route("/CSE305/checkout/", methods=["POST"])
def CSE305_checkout():
    try:
        #Checking if the current person is already logged in as a User
        if('UserID' in session):
            #Checking to see if the user exists in the DB -- If so, we should grab the users information
            current_user = None
            try:
                values = (session['UserID'],)
                current_user = query_db_target("SELECT * FROM User WHERE UserID=?", CSE305_DATABASE, values)
                #If there are no users with this userid, we should redirect and clear the session
                if(len(current_user) == 0):
                    session.clear()
                    return redirect(url_for('CSE305_eBoyHomepage'))
            except Exception as query_exception:
                return(str(query_exception))

            #Getting the arguments
            UserID=session['UserID']

            #Creating the connection & cursor
            con, cur = begin_transaction(CSE305_DATABASE)
            OrderID = None
            #Beginning the transaction!
            try:
                cur.execute("BEGIN TRANSACTION", ())

                #Getting the OrderID
                cur.execute("SELECT MAX(OrderID) FROM Orders", ())
                OrderID = cur.fetchone()

                if( OrderID['MAX(OrderID)'] == None ):
                    OrderID = 1
                else:
                    OrderID = OrderID['MAX(OrderID)'] + 1

                #Getting all the items for the current user's shopping cart
                values = (UserID,)
                cur.execute("SELECT `ItemID`, `Quantity` FROM ShoppingCart WHERE `UserID`=?", values)
                ShoppingCartItems = cur.fetchall()

                orderTime = datetime.now()
                for item in ShoppingCartItems:
                    values = (OrderID, UserID, item['ItemID'], item['Quantity'], orderTime, request.form['shippingInfo'], orderTime + timedelta(days=4), request.form['address'],)
                    cur.execute("INSERT INTO Orders(OrderID, UserID, ItemID, Quantity, OrderDateTime, ShippingInfo, DeliveryDateTime, Address) VALUES(?, ?, ?, ?, ?, ?, ?, ?)", values)
                    #Checking if the rowcount is less than or equal to 0
                    if(cur.rowcount <= 0):
                        con.rollback()
                        con.close()
                        return("Fail to insert into Order")

                values = (UserID,)
                cur.execute("DELETE FROM ShoppingCart WHERE UserID=?", values)
                if(cur.rowcount <= 0):
                    con.rollback()
                    con.close()
                    return("Fail to delete shopping cart rows")
                con.commit()
                con.close()
            except Exception as query_exception:
                con.rollback()
                return(str(query_exception))
            con.close()

            #At this point, we have all the user's information and we know they exist!
            return("success")
        else:
            return("Failure - User is not logged in with a valid account!")
    except Exception as e:
        return("Failure" + str(e))

@app.route("/CSE305/change_permissions/", methods=["POST"])
def CSE305_change_permissions():
    try:
        #Checking if the current person is already logged in as an employee
        if('EmployeeID' in session):
            #Checking to see if the user exists in the DB -- If so, we should grab the users information
            current_employee = None
            try:
                values = (session['EmployeeID'],)
                current_employee = query_db_target("SELECT E.EmployeeID, E.RoleID, E.Username, R.RoleName, R.Rank, E.ManagerID, M.Username as ManagerUsername FROM Employee E LEFT JOIN Role R ON E.RoleID=R.RoleID LEFT JOIN Employee M ON E.ManagerID=M.EmployeeID WHERE E.EmployeeID=?;", CSE305_DATABASE, values)
                #If there are no users with this userid, we should redirect and clear the session
                if(len(current_employee) == 0):
                    session.clear()
                    return redirect(url_for('CSE305_eBoyEmployeeHomepage'))
            except Exception as query_exception:
                return(str(query_exception))

            #At this point, we have all the user's information and we know they exist!
            permissions = None
            try:
                #Getting the permissions for the user
                values = (current_employee[0]['RoleID'],)
                permissions = query_db_target("SELECT HasPermission.PermissionID, PermissionDescription, PermissionShort FROM HasPermission LEFT JOIN Permissions ON HasPermission.PermissionID=Permissions.PermissionID WHERE HasPermission.RoleID=?;", CSE305_DATABASE, values)
            except Exception as query_exception:
                return(str(query_exception))

            role = str(request.form['Role'])
            permissions = []
            for requestArgument in request.form:
                if("Permission" in str(requestArgument)):
                    temp = []
                    temp.append(str(requestArgument).split("-")[1])
                    temp.append(request.form[requestArgument])
                    permissions.append(temp)
            # return(str(permissions))

            #Beginning the transaction
            #Creating the connection & cursor
            con, cur = begin_transaction(CSE305_DATABASE)

            #Beginning the transaction!
            try:
                cur.execute("BEGIN TRANSACTION", ())

                #Delete from the HasPermission Relation
                # values = (role, str(current_employee[0]['RoleID']),)
                # cur.execute("DELETE FROM HasPermission WHERE RoleID=? AND PermissionID IN (SELECT PermissionID FROM HasPermission P WHERE P.RoleID=?)", values)
                values = (role, str(current_employee[0]['RoleID']),)
                cur.execute("DELETE FROM HasPermission WHERE RoleID=? AND PermissionID IN (SELECT P.PermissionID FROM HasPermission P WHERE P.RoleID=?);", values)
                #Checking if the rowcount is less than or equal to 0
                if(cur.rowcount <= 0):
                    con.rollback()
                    con.close()
                    return("Failed to delete from HasPermission")

                #Inserting the new values into HasPermission
                for permission in permissions:
                    if(str(permission[1]) == "true"):
                        values = (role, int(permission[0]))
                        cur.execute("INSERT INTO HasPermission VALUES (?, ?)", values)
                        #Checking if the rowcount is less than or equal to 0
                        if(cur.rowcount <= 0):
                            con.rollback()
                            con.close()
                            return("Fail to insert into HasPermission")
                con.commit()
            except Exception as query_exception:
                con.rollback()
                return(str(query_exception))
            con.close()

            # return(str(current_employee) + "<br><br>" + str(permissions) + "<br><br>" + str(subordinates))

            return("Success")
        else:
            return("Failure")
    except Exception as e:
        return(str(e))

@app.route("/CSE305/remove_user/", methods=["POST"])
def CSE305_remove_user():
    try:
        #Checking if the current person is already logged in as an employee
        if('EmployeeID' in session):
            #Checking to see if the user exists in the DB -- If so, we should grab the users information
            current_employee = None
            try:
                values = (session['EmployeeID'],)
                current_employee = query_db_target("SELECT E.EmployeeID, E.RoleID, E.Username, R.RoleName, R.Rank, E.ManagerID, M.Username as ManagerUsername FROM Employee E LEFT JOIN Role R ON E.RoleID=R.RoleID LEFT JOIN Employee M ON E.ManagerID=M.EmployeeID WHERE E.EmployeeID=?;", CSE305_DATABASE, values)
                #If there are no users with this userid, we should redirect and clear the session
                if(len(current_employee) == 0):
                    session.clear()
                    return redirect(url_for('CSE305_eBoyEmployeeHomepage'))
            except Exception as query_exception:
                return(str(query_exception))

            #Beginning the transaction
            #Creating the connection & cursor
            con, cur = begin_transaction(CSE305_DATABASE)

            #Beginning the transaction!
            try:
                cur.execute("BEGIN TRANSACTION", ())

                values = (str(request.form["UserID"]), )
                cur.execute("DELETE FROM User WHERE UserID = ?;", values)
                #Checking if the rowcount is less than or equal to 0
                if(cur.rowcount <= 0):
                    con.rollback()
                    con.close()
                    return("Failed to delete from User")

                cur.execute("DELETE FROM Inventory WHERE Inventory.ItemID IN (SELECT Post.ItemID FROM Post WHERE Post.UserID = ?);", values)
                if(cur.rowcount <= 0):
                    con.rollback()
                    con.close()
                    return("Failed to delete from inventory")
                con.commit()
            except Exception as query_exception:
                con.rollback()
                return(str(query_exception))
            con.close()

            return("Success")
        else:
            return("Failure")
    except Exception as e:
        return(str(e))

@app.route("/CSE305/remove_item/", methods=["POST"])
def CSE305_remove_item():
    try:
        #Checking if the current person is already logged in as an employee
        if('EmployeeID' in session):
            #Checking to see if the user exists in the DB -- If so, we should grab the users information
            current_employee = None
            try:
                values = (session['EmployeeID'],)
                current_employee = query_db_target("SELECT E.EmployeeID, E.RoleID, E.Username, R.RoleName, R.Rank, E.ManagerID, M.Username as ManagerUsername FROM Employee E LEFT JOIN Role R ON E.RoleID=R.RoleID LEFT JOIN Employee M ON E.ManagerID=M.EmployeeID WHERE E.EmployeeID=?;", CSE305_DATABASE, values)
                #If there are no users with this userid, we should redirect and clear the session
                if(len(current_employee) == 0):
                    session.clear()
                    return redirect(url_for('CSE305_eBoyEmployeeHomepage'))
            except Exception as query_exception:
                return(str(query_exception))

            try:
                values = (str(request.form["ItemID"]), )
                query = post_db_target("DELETE FROM Inventory WHERE ItemID = ?;", CSE305_DATABASE, values)
            except Exception as query_exception:
                return("Unable to delete the item!" + str(query_exception))
            return("Success")
        else:
            return("Failure")
    except Exception as e:
        return(str(e))

@app.route("/CSE305/update_item/", methods=["POST"])
def CSE305_update_item():
    try:
        #Checking if the current person is already logged in as an employee
        if('EmployeeID' in session):
            #Checking to see if the user exists in the DB -- If so, we should grab the users information
            current_employee = None
            try:
                values = (session['EmployeeID'],)
                current_employee = query_db_target("SELECT E.EmployeeID, E.RoleID, E.Username, R.RoleName, R.Rank, E.ManagerID, M.Username as ManagerUsername FROM Employee E LEFT JOIN Role R ON E.RoleID=R.RoleID LEFT JOIN Employee M ON E.ManagerID=M.EmployeeID WHERE E.EmployeeID=?;", CSE305_DATABASE, values)
                #If there are no users with this userid, we should redirect and clear the session
                if(len(current_employee) == 0):
                    session.clear()
                    return redirect(url_for('CSE305_eBoyEmployeeHomepage'))
            except Exception as query_exception:
                return(str(query_exception))

            #Creating the connection & cursor
            con, cur = begin_transaction(CSE305_DATABASE)

            #Beginning the transaction!
            try:
                cur.execute("BEGIN TRANSACTION", ())
                #Inserting into the Item Relation
                values = (request.form['itemPrice'], request.form['itemDesc'], request.form['itemName'], request.form['itemID'])
                cur.execute("UPDATE Item SET Price=?, Description=?, Name=? WHERE Item.ItemID=?", values)
                #Checking if the rowcount is less than or equal to 0
                if(cur.rowcount <= 0):
                    con.rollback()
                    con.close()
                    return("Fail to insert into Item")

                #Inserting into the Inventory Relation
                values = (request.form['itemQuantity'], request.form['itemID'])
                cur.execute("UPDATE Inventory SET Quantity=? WHERE Inventory.ItemID=?", values)
                #Checking if the rowcount is less than or equal to 0
                if(cur.rowcount <= 0):
                    con.rollback()
                    con.close()
                    return("Fail to insert into Inventory")

                con.commit()
            except Exception as query_exception:
                con.rollback()
                return(str(query_exception))
            con.close()
            return("Success")
        else:
            return("Failure")
    except Exception as e:
        return(str(e))

@app.route("/CSE305/remove_review/", methods=["POST"])
def CSE305_remove_review():
    try:
        #Checking if the current person is already logged in as an employee
        if('EmployeeID' in session):
            #Checking to see if the user exists in the DB -- If so, we should grab the users information
            current_employee = None
            try:
                values = (session['EmployeeID'],)
                current_employee = query_db_target("SELECT E.EmployeeID, E.RoleID, E.Username, R.RoleName, R.Rank, E.ManagerID, M.Username as ManagerUsername FROM Employee E LEFT JOIN Role R ON E.RoleID=R.RoleID LEFT JOIN Employee M ON E.ManagerID=M.EmployeeID WHERE E.EmployeeID=?;", CSE305_DATABASE, values)
                #If there are no users with this userid, we should redirect and clear the session
                if(len(current_employee) == 0):
                    session.clear()
                    return redirect(url_for('CSE305_eBoyEmployeeHomepage'))
            except Exception as query_exception:
                return(str(query_exception))

            try:
                values = (str(request.form["ReviewID"]), )
                query = post_db_target("DELETE FROM Review WHERE ReviewID = ?;", CSE305_DATABASE, values)
            except Exception as query_exception:
                return("Unable to delete the review!" + str(query_exception))
            return("Success")
        else:
            return("Failure")
    except Exception as e:
        return(str(e))

@app.route("/CSE305/remove_employee/", methods=["POST"])
def CSE305_remove_employee():
    try:
        #Checking if the current person is already logged in as an employee
        if('EmployeeID' in session):
            #Checking to see if the user exists in the DB -- If so, we should grab the users information
            current_employee = None
            try:
                values = (session['EmployeeID'],)
                current_employee = query_db_target("SELECT E.EmployeeID, E.RoleID, E.Username, R.RoleName, R.Rank, E.ManagerID, M.Username as ManagerUsername FROM Employee E LEFT JOIN Role R ON E.RoleID=R.RoleID LEFT JOIN Employee M ON E.ManagerID=M.EmployeeID WHERE E.EmployeeID=?;", CSE305_DATABASE, values)
                #If there are no users with this userid, we should redirect and clear the session
                if(len(current_employee) == 0):
                    session.clear()
                    return redirect(url_for('CSE305_eBoyEmployeeHomepage'))
            except Exception as query_exception:
                return(str(query_exception))

            try:
                values = (str(request.form["EmployeeID"]), )
                query = post_db_target("DELETE FROM Employee WHERE EmployeeID = ?;", CSE305_DATABASE, values)
            except Exception as query_exception:
                return("Unable to delete the employee!" + str(query_exception))
            return("Success")
        else:
            return("Failure")
    except Exception as e:
        return(str(e))









#Below is the location of the database on the server
HACKHEALTH_DATABASE = '/var/www/FlaskApp/FlaskApp/HackHealth.db'

@app.route("/HackHealth/login/", methods=["POST"])
def HackHealth_Login():
    try:
        username = str(request.form["login_username"])
        password = str(request.form["login_password"])

        values = (username,)
        users = query_db_target("SELECT * FROM User WHERE Username = ?", HACKHEALTH_DATABASE, values)
        if((len(users) == 1) and (str(users[0]['Password']) == password)):
            if():
                response = {
                    "Status"  : "success",
                    "Message" : {
                        "DisplayMessage" : "Successfully logged in!",
                        "Username" : users[0]['Username']
                    }
                }
                response = json.loads(response)
                return(response)
        raise Exception("Invalid Credentials!")
    except Exception as e:
        response = {
            "Status"  : "failure",
            "Message" : {
                "DisplayMessage" : exception,
            }
        }
        response = json.loads(response)
        return(response)

@app.route("/HackHealth/register/", methods=["POST"])
def HackHealth_Register():
    try:
        response = {
            "Status"  : "success",
            "Message" : {
                "DisplayMessage" : "Succesfully registered!",
            }
        }
        response = json.loads(response)
        return(response)

        username        = str(request.form["register_username"])
        firstname       = str(request.form["register_firstname"])
        lastname        = str(request.form["register_lastname"])
        password        = str(request.form["register_password"])
        profile_picture = str(request.form["register_profile_picture"])

        response = {
            "Status"  : "success",
            "Message" : {
                "DisplayMessage" : "Succesfully registered!",
            }
        }
        response = json.loads(response)
        return(response)


        values = (username,)
        users = query_db_target("SELECT * FROM User WHERE Username = ?", HACKHEALTH_DATABASE, values)
        if(len(users) != 0):
            raise Exception("Username is already in user!")
        else:
            values = (username, firstname, lastname, password, profile_picture)
            users = query_db_target("INSERT INTO User VALUES (?, ?, ?, ?, ?)", HACKHEALTH_DATABASE, values)

            response = {
                "Status"  : "success",
                "Message" : {
                    "DisplayMessage" : "Succesfully registered!",
                    "Username" : username
                }
            }
            response = json.loads(response)
            return(response)
    except Exception as e:
        response = {
            "Status"  : "failure",
            "Message" : {
                "DisplayMessage" : exception,
            }
        }
        response = json.loads(response)
        return(response)

@app.route("/HackHealth/activity/", methods=["GET", "POST"])
def HackHealth_Activity():
    if(request.method == "GET"):
        try:
            username         = str(request.form["username"])

            values = (username,)
            activities = query_db_target("SELECT UserActivity WHERE UserActivity.Username IN (SELECT * FROM Friend WHERE Username_1 = ?) SORT BY UserActivity.UploadTime", HACKHEALTH_DATABASE, values)

            response = {
                "Status"  : "success",
                "Message" : {
                    "DisplayMessage" : activities
                }
            }
            response = json.loads(response)
            return(response)
        except Exception as e:
            response = {
                "Status"  : "failure",
                "Message" : {
                    "DisplayMessage" : exception,
                }
            }
            response = json.loads(response)
            return(response)
    elif(request.method == "POST"):
        try:
            username         = str(request.form["username"])
            activity_picture = str(request.form["activity_picture"])

            values = (username, activity_picture)
            users = query_db_target("INSERT INTO UserActivity(Username, ImageURL) VALUES(?, ?)", HACKHEALTH_DATABASE, values)
            response = {
                "Status"  : "success",
                "Message" : {
                    "DisplayMessage" : "Activity Submitted!",
                }
            }
            response = json.loads(response)
            return(response)
        except Exception as e:
            response = {
                "Status"  : "failure",
                "Message" : {
                    "DisplayMessage" : exception,
                }
            }
            response = json.loads(response)
            return(response)

@app.route("/HackHealth/activity/comment/", methods=["POST"])
def HackHealth_Activity_Comment():
    try:
        activity_id = str(request.form["activity_id"])
        username    = str(request.form["username"])
        description = str(request.form["description"])

        values = (activity_id, username, description)
        users = query_db_target("INSERT INTO ActivityComments(ActivityID, Username, Description) VALUES(?, ?, ?)", HACKHEALTH_DATABASE, values)
        response = {
            "Status"  : "success",
            "Message" : {
                "DisplayMessage" : "Comment Submitted!",
            }
        }
        response = json.loads(response)
        return(response)
    except Exception as e:
        response = {
            "Status"  : "failure",
            "Message" : {
                "DisplayMessage" : exception,
            }
        }
        response = json.loads(response)
        return(response)











if __name__ == "__main__":
    app.run()
