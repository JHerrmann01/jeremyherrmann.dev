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

display = Display(visible=0, size=(800, 600))
display.start()

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
        #Going to the login page
        self.browser.get('https://www.instagram.com/accounts/login')
        self.browser.implicitly_wait(180)


        #Filling the inputs
        self.browser.find_element_by_xpath("//input[@name='username']").send_keys(self.email)
        self.browser.find_element_by_xpath("//input[@name='password']").send_keys(self.password)

        #Logging in
        logInButton = self.browser.find_element_by_xpath("//button[contains(.,'Log in')]")
        logInButton.click()
        time.sleep(5)

        self.loggedInBrowser = True

    def apiSignIn(self):
        #Logging into the API
        self.api = InstagramAPI(self.email, self.password)
        response = self.api.login()
        time.sleep(5)

        if(str(response) is "None"):
            self.loggedInAPI = False
        elif(str(response) is "True"):
            self.loggedInAPI = True

    def followWithUsername(self, username):
        try:
            #Going to the user's instagram account
            self.browser.get('https://www.instagram.com/' + username + '/')
            time.sleep(2)
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

    def followAction(self, listToFollow):
        #Initializing a counter
        count = 0
        #Traversing the list of users
        for user in listToFollow:
            #Getting the current user's username
            username = str(user['Username'])
            if(self.followWithUsername(username)):
                #Updating the user in the database so that we don't follow them again
                post_db_target("UPDATE `tUsersToFollow` SET `HasFollowed` = 1 WHERE `UserID` = '" + str(user['UserID']) + "'", DATABASE)
                #Incrementing the current count
                count += 1
            #Generating a random time to sleep for
            randomTime = random.randint(FOLLOW_SLEEP_MIN, FOLLOW_SLEEP_MAX) / 100
            time.sleep(randomTime)

            #Every X follows, we want to sleep for a little bit
            if((count % FOLLOW_SLEEP_LONG_FREQUENCY == 0) and (count != 0)):
                time.sleep(FOLLOW_SLEEP_LONG / 100)

    def unfollowAction(self, quantity):
        #Getting the users that I am currently following using the InstagramAPI
        listToUnfollow = self.getFollowing()
        #Initializing a counter
        count = 0
        #Traversing the list of users
        for user in listToUnfollow:
            #When the current count == quantity we want to stop unfollowing users
            if(count == quantity):
                break

            #Getting the current user's userID & username
            userID = str(user['pk'])
            username = str(user['username'])

            if(UNFOLLOW_WITH_API):
                if(self.unfollowWithAPI(userID)):
                    #Incrementing the current count
                    count += 1
            else:
                if(self.unfollowWithUsername(username)):
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
                caption += hashtag

            caption = caption + "\n#sunset #sunsetlovers #sunsets #nature #sky #ig #photooftheday #picoftheday #sunrise #sunrisephotography #greatlandscapes_oftheworld #landscapelovers #sunset_captures #landscape_capture #sunsetlover #landscapephotography #landscapelover #bestplaces #landscape_collection #sunsetphotography #landscape_specialist #sunset_stream #sunsetchaser"
            response = self.api.uploadPhoto(imageFilename, caption=caption)
            return(str(response))
        except Exception as e:
            return(str(e))

    def closeBrowser(self):
        if(self.loggedInAPI):
            self.api.logout()
        if(self.loggedInBrowser):
            self.browser.close()

    def __exit__(self, exc_type, exc_value, traceback):
        self.closeBrowser()


#Grabbing the raw HTML for a specified URL
def retrieveWebPageHTML(Url):
    user_agents=['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0',
                           'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0',
                           'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533+ \(KHTML, like Gecko) Element Browser 5.0',
                           'IBM WebExplorer /v0.94', 'Galaxy/1.0 [en] (Mac OS X 10.5.6; U; en)',
                           'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
                           'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
                           'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) \Version/6.0 Mobile/10A5355d Safari/8536.25',
                           'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) \Chrome/28.0.1468.0 Safari/537.36',
                           'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; TheWorld)']
    headers={'User-Agent':user_agents,}
    #Assembling the request which we will make the the specified url
    request=urllib2.Request(Url,None,headers)
    #Making the request, and returning the response
    response = urllib2.urlopen(request).read()
    return(response)

#Given an HTML string, return all the images found inside the HTML
def parseHTML(html):
    soup = BeautifulSoup(html,'html.parser')
    return(soup.findAll('img', class_="photo-item__img"))

#Given a list of images, filter out profile_pictures/icons/etc
def refineImageURLS(imgList):
    properURLS = []
    for img in imgList:
        img = img.get('src')
        #We want to filter out anything that is considered an "asset"
        if('assets' not in img.split("/")):
            #Appending the raw url, removing the filters from the end
            properURLS.append(img.split("?")[0])
    return properURLS

#Downloading an image and storing it locally
def downloadFile(ImageURL):
    #Retrieving the HTML from the Url
    image = retrieveWebPageHTML(ImageURL)
    #Grabbing the extension from the original url so that we don't change the type of file
    extension = ImageURL.split(".")[len(ImageURL.split("."))-1]
    #Creating the filename where we will store the image
    imageFilename = "/var/www/FlaskApp/FlaskApp/RecentImage" + "." + extension
    #Writing the image
    output = open(imageFilename,"wb")
    output.write(image)
    output.close()
    return(imageFilename)

try:
    #Creating a InstagramBot and logging in
    IGBot = InstagramBot(EMAIL, PASSWORD)
    IGBot.apiSignIn()

    print("done signing in!")

    #Grabbing the ImageURL & Caption for the post
    # ImageURL = str(request.form['URL'])
    # Caption = str(request.form['Caption'])
    ImageURL = "https://images.pexels.com/photos/315987/pexels-photo-315987.jpeg"
    Caption = "You can never cross the ocean until you have the courage to lose sight of the shore."

    #Downloading the image and storing the directory of the image in imageFilename
    imageFilename = downloadFile(ImageURL)

    print("downloaded file")

    #Grabbing the hashtags
    hashtags = []

    #Posting the image with the caption & set of hashtags we want to append
    response = IGBot.postImage(imageFilename, Caption, hashtags)

    print("done posting image")

    #Removing the image from our directory
    os.remove(imageFilename)

    if(response == "Success"):
        #Adding the ImageURL to our database
        values = (ImageURL, time.time())
        # post_db_target("INSERT INTO tUsedImages (imageURL, time) VALUES (?, ?)", DATABASE, values)

    #Constructing a response
    data = {"Response":str(response)}
    print(str(data))
    # response = jsonify(data)
    # response.status_code = 200
    # return(response)
except Exception as e:
    data = {"Response":str(e)}
    print(str(data))
    # response = jsonify(data)
    # response.status_code = 200
    # return(response)
