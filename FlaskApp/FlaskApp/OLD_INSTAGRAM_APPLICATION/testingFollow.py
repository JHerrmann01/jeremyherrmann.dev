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

EMAIL = "satisfyingsunsets@gmail.com"
PASSWORD = "Laralamp"
# EMAIL = "earth_photos_daily"
# PASSWORD = "Herrmann001"

FOLLOW_SLEEP_MIN = 1500
FOLLOW_SLEEP_MAX = 2000
FOLLOW_SLEEP_LONG = 2200
FOLLOW_SLEEP_LONG_FREQUENCY = 11

RELOGIN_DELAY = 60*60*10

#Page indices to grab images from
FIRST_IMAGE_PAGE = 2
LAST_IMAGE_PAGE = 8

UNFOLLOW_WITH_API = True

DATABASE = '/var/www/FlaskApp/FlaskApp/instagramUsers.db'

display = Display(visible=0, size=(800, 600))
display.start()

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

class InstagramBot():
    def __init__(self, email, password):
        self.browserProfile = webdriver.ChromeOptions()
        self.browserProfile.add_argument('--no-sandbox')
        self.browser = webdriver.Chrome(executable_path='../../../../../../../home/chromedriver', chrome_options=self.browserProfile)
        self.loggedInAPI = False
        self.loggedInBrowser = False
        self.email = email
        self.password = password

    def signIn(self):
        print("Browser Login!")
        #Going to the login page
        self.browser.get('https://www.instagram.com/accounts/login')
        self.browser.implicitly_wait(180)

        print("Title: " +  str((self.browser.title).encode('utf-8').strip()))

        #Checking if the page is the login page
        isNotLoggedIn = "Login" in str((self.browser.title).encode('utf-8').strip())
        if(isNotLoggedIn):
            #Filling the inputs
            self.browser.find_element_by_xpath("//input[@name='username']").send_keys(self.email)
            self.browser.find_element_by_xpath("//input[@name='password']").send_keys(self.password)

            #Logging in
            logInButton = self.browser.find_element_by_xpath("//button[contains(.,'Log in')]")
            logInButton.click()
            time.sleep(5)
            print("Updated Title: " +  str((self.browser.title).encode('utf-8').strip()))

        self.loggedInBrowser = True

    def apiSignIn(self):
        #Logging into the API
        self.api = InstagramAPI(self.email, self.password)
        response = self.api.login()
        time.sleep(5)
        print("Api Login!")

        if(str(response) is "None"):
            self.loggedInAPI = False
        elif(str(response) is "True"):
            self.loggedInAPI = True

        return(self.loggedInAPI)

    def followWithUsername(self, username):
        try:
            #Going to the user's instagram account
            self.browser.get('https://www.instagram.com/' + username + '/')
            time.sleep(2)
            print("Instagram User Page: " +  str((self.browser.title).encode('utf-8').strip()))
            #Finding the follow button & Clicking the button if it's the correct button
            followButton = self.browser.find_element_by_css_selector('button')
            if (followButton.text != 'Following'):
                followButton.click()
                time.sleep(2)
                return True
            else:
                return False
        except Exception as e:
            return(str(e))

    def unfollowWithUsername(self, username):
        #Going to the user's instagram account
        self.browser.get('https://www.instagram.com/' + username + '/')
        time.sleep(2)
        #Finding the 'Following' button & Clicking the button if it's the correct button
        followButton = self.browser.find_element_by_css_selector('button')
        if (followButton.text == 'Following'):
            followButton.click()
            time.sleep(2)
            #Waiting for the prompt to open, then clicking the confirm unfollow button
            confirmButton = self.browser.find_element_by_xpath('//button[text() = "Unfollow"]')
            confirmButton.click()
            return True
        else:
            return False

    def unfollowWithAPI(self, userID):
        #Unfollowing a specified user by UserID
        self.api.unfollow(userID)
        return True

    def getFollowing(self):
        #Getting the followers from the API & Returning them
        followers = self.api.getTotalFollowings(self.api.username_id)
        return followers

    def getFollowed(self):
        #Getting the followers from the API & Returning them
        followers = self.api.getTotalFollowers(self.api.username_id)
        return followers

    def followAction(self, listToFollow):
        #Initializing a counter
        count = 0
        #Traversing the list of users
        for user in listToFollow:
            #Getting the current user's username
            username = str(user['Username'])
            print(str(username))
            if(self.followWithUsername(username)):
                #Updating the user in the database so that we don't follow them again
                post_db_target("UPDATE `tUsersToFollow` SET `HasFollowed` = 1 WHERE `UserID` = '" + str(user['UserID']) + "'", DATABASE)
                #Incrementing the current count
                count += 1
            #Generating a random time to sleep for
            randomTime = random.randint(FOLLOW_SLEEP_MIN, FOLLOW_SLEEP_MAX) / 100
            time.sleep(randomTime)
            print("\tShort Sleep")

            #Every X follows, we want to sleep for a little bit
            if((count % FOLLOW_SLEEP_LONG_FREQUENCY == 0) and (count != 0)):
                print("\t\tLong Sleep")
                time.sleep(FOLLOW_SLEEP_LONG / 100)

    def unfollowAction(self, quantity, unfollowAnyone):
        #Getting the users that I am currently following using the InstagramAPI
        if(UNFOLLOW_WITH_API):
            if(unfollowAnyone):
                listToUnfollow = query_db_target("SELECT GROUP_CONCAT(userID) FROM tCurrentlyFollowing WHERE (userID NOT IN (SELECT `userID` FROM tWhitelist)) AND (`haveUnfollowed` = 0)", DATABASE)[0]
            else:
                listToUnfollow = query_db_target("SELECT GROUP_CONCAT(userID) FROM tCurrentlyFollowing WHERE (userID NOT IN (SELECT `userID` FROM tWhitelist)) AND (userID NOT IN (SELECT `userID` FROM tCurrentlyFollowed)) AND (`haveUnfollowed` = 0)", DATABASE)[0]
            if((str(listToUnfollow['GROUP_CONCAT(userID)']) != "None")):
                listToUnfollow = listToUnfollow['GROUP_CONCAT(userID)'].split(",")
            else:
                listToUnfollow = []
        else:
            if(unfollowAnyone):
                listToUnfollow = query_db_target("SELECT GROUP_CONCAT(username) FROM tCurrentlyFollowing WHERE (username NOT IN (SELECT `username` FROM tWhitelist)) AND (`haveUnfollowed` = 0)", DATABASE)[0]
            else:
                listToUnfollow = query_db_target("SELECT GROUP_CONCAT(username) FROM tCurrentlyFollowing WHERE (username NOT IN (SELECT `username` FROM tWhitelist)) AND (username NOT IN (SELECT `username` FROM tCurrentlyFollowed)) AND (`haveUnfollowed` = 0)", DATABASE)[0]
            if((str(listToUnfollow['GROUP_CONCAT(username)']) != "None")):
                listToUnfollow = listToUnfollow['GROUP_CONCAT(username)'].split(",")
            else:
                listToUnfollow = []

        #Initializing a counter
        count = 0
        #Traversing the list of users
        for user in listToUnfollow:
            #When the current count == quantity we want to stop unfollowing users
            if(count == quantity):
                break
            #Getting the current user's userID & username
            # userID = str(user['pk'])
            # username = str(user['username'])

            if(UNFOLLOW_WITH_API):
                if(self.unfollowWithAPI(user)):
                    post_db_target("UPDATE `tCurrentlyFollowing` SET `haveUnfollowed` = 1 WHERE `userID` = '" + str(user) + "'", DATABASE)
                    #Incrementing the current count
                    count += 1
            else:
                if(self.unfollowWithUsername(user)):
                    post_db_target("UPDATE `tCurrentlyFollowing` SET `haveUnfollowed` = 1 WHERE `username` = '" + str(user) + "'", DATABASE)
                    #Incrementing the current count
                    count += 1

            #Generating a random time to sleep for
            randomTime = random.randint(FOLLOW_SLEEP_MIN, FOLLOW_SLEEP_MAX) / 100
            time.sleep(randomTime)

            #Every X follows, we want to sleep for a little bit
            if((count % FOLLOW_SLEEP_LONG_FREQUENCY == 0) and (count != 0)):
                time.sleep(FOLLOW_SLEEP_LONG / 100)

    def postImage(self, imageFilename, caption, hashtagArray):
        try:
            caption = caption + "\n"
            for hashtag in hashtagArray:
                caption = caption + "#" + hashtag + " "

            # caption = caption + "\n#sunset #sunsetlovers #sunsets #nature #sky #ig #photooftheday #picoftheday #sunrise #sunrisephotography #greatlandscapes_oftheworld #landscapelovers #sunset_captures #landscape_capture #sunsetlover #landscapephotography #landscapelover #bestplaces #landscape_collection #sunsetphotography #landscape_specialist #sunset_stream #sunsetchaser #gf_skies #satisfyingsunsets"
            self.api.uploadPhoto(imageFilename, caption=caption)
            return("Success")
        except Exception as e:
            return(str(e))

    def lookUpUser(self, username):
        try:
            self.api.searchUsername(username)
            username_id = self.api.LastJson["user"]["pk"]
            return(True, str(username_id))
        except Exception as e:
            return(False, str(e))

    def closeBrowser(self):
        if(self.loggedInBrowser):
            self.browser.close()

    def __exit__(self, exc_type, exc_value, traceback):
        self.closeBrowser()


STATIC_INSTAGRAM_BOT = InstagramBot(EMAIL, PASSWORD)
STATIC_INSTAGRAM_BOT.apiSignIn()
STATIC_INSTAGRAM_BOT.signIn()
lastSignInTime = time.time()

#The thread which will Initialize the IGBot to follow accounts
def followingThread(Quantity, IGBot):
    try:
        #Grabbing a list of people to follow from the database with the max = quantity
        listToFollow = query_db_target("SELECT * FROM `tUsersToFollow` WHERE `HasFollowed` = 0 LIMIT " + str(Quantity), DATABASE)

        print(str(listToFollow))

        #Calculating the amount of time it will take to follow this many users(May be less than quantity)
        followingTime = ((FOLLOW_SLEEP_MAX / 100) * len(listToFollow)) + (int(len(listToFollow) / FOLLOW_SLEEP_LONG_FREQUENCY) * (FOLLOW_SLEEP_LONG / 100))

        #Calculating the time which the following process will be done.
        currentTime = int(time.time())
        values = "Follow", Quantity, currentTime, (currentTime + followingTime)
        post_db_target("INSERT INTO tActions (action, quantity, beginTime, endTime) VALUES (?, ?, ?, ?)", DATABASE, values)

        #Telling the Instagram Bot to follow everyone in the list
        IGBot.followAction(listToFollow)
    except Exception as e:
        #Emailing myself about the error
        return(str(e))

#The endpoint which will be used to indicate how many people to follow
def follow():
    try:
        #Getting the current time
        currentTime = int(time.time())

        #Checking if there is an action that will end later than the current time
        allActions = query_db_target("SELECT * FROM tActions WHERE `endTime` > '" + str(currentTime) + "'", DATABASE)
        if(len(allActions) == 0):
            Quantity = 20
            # if(request.method == "GET"):
            #     Quantity = int(request.args.get('Quantity'))
            # elif(request.method == "POST"):
            #     Quantity = int(request.form['Quantity'])
            # if(Quantity is None):
            #     #Constructing a response
            #     data = {'Response' : "No Arguments"}
            #     print(str(data))
            #     return(str(data))

            global STATIC_INSTAGRAM_BOT
            global lastSignInTime

            isSuccessful, userID = STATIC_INSTAGRAM_BOT.lookUpUser("instagram")
            if(not isSuccessful):
                # STATIC_INSTAGRAM_BOT.closeBrowser()
                # STATIC_INSTAGRAM_BOT = InstagramBot(EMAIL, PASSWORD)
                STATIC_INSTAGRAM_BOT.apiSignIn()
                STATIC_INSTAGRAM_BOT.signIn()
                lastSignInTime = time.time()
                print("Not successful! Relogging...")

            #If we are not currently performing any actions(Following/Unfollowing/Posting) then we want to proceed with this by starting the followingThread
            thread = threading.Thread(target=followingThread, args=(Quantity, STATIC_INSTAGRAM_BOT,), name='followingThread')
            thread.start()

            #Constructing a response
            data = {'Response' : "Done following " + str(Quantity) + " people."}
            print(str(data))
            return(str(data))
        else:
            #Constructing a response
            data = {'Response' : "Currently Following/Unfollowing People"}
            print(str(data))
            return(str(data))
    except Exception as e:
        #Need to email myself about the error
        #Constructing a response
        data = {'Response' : str(e)}
        print(str(data))
        return(str(data))

if __name__ == "__main__":
    follow()
