
# EMAIL = "satisfyingsunsets@gmail.com"
# PASSWORD = "Laralamp"
# # EMAIL = "earth_photos_daily"
# # PASSWORD = "Herrmann001"
#
# FOLLOW_SLEEP_MIN = 1500
# FOLLOW_SLEEP_MAX = 2000
# FOLLOW_SLEEP_LONG = 2200
# FOLLOW_SLEEP_LONG_FREQUENCY = 11
#
# RELOGIN_DELAY = 60*60*10
#
# #Page indices to grab images from
# FIRST_IMAGE_PAGE = 2
# LAST_IMAGE_PAGE = 8
#
# UNFOLLOW_WITH_API = True
# FOLLOW_WITH_API = True
#
# DATABASE = '/var/www/FlaskApp/FlaskApp/instagramUsers.db'
#
# display = Display(visible=0, size=(800, 600))
# display.start()
#
# def dict_factory(cursor, row):
#     d = {}
#     for idx, col in enumerate(cursor.description):
#         d[col[0]] = row[idx]
#     return d
#
# # Query will be used to get information from the database #
# def query_db_target(query, database, args=(), dictionary = True):
#     con = sqlite3.connect(database)
#     if dictionary:
#         con.row_factory = dict_factory
#     cur = con.cursor()
#     cur.execute(query, args)
#     rv = cur.fetchall()
#     con.commit()
#     con.close()
#     return rv
#
# # Post will be used to change/input information into the database #
# def post_db_target(query, database, args=()):
#     con = sqlite3.connect(database)
#     cur = con.cursor()
#     cur.execute(query, args)
#     con.commit()
#     con.close()
#
# class InstagramBot():
#     def __init__(self, email, password):
#         if((not FOLLOW_WITH_API) or (not UNFOLLOW_WITH_API)):
#             self.browserProfile = webdriver.ChromeOptions()
#             self.browserProfile.add_argument('--no-sandbox')
#             self.browser = webdriver.Chrome(executable_path='../../../../../../../home/chromedriver', chrome_options=self.browserProfile)
#         self.loggedInAPI = False
#         self.loggedInBrowser = False
#         self.email = email
#         self.password = password
#
#     def signIn(self):
#         #Going to the login page
#         self.browser.get('https://www.instagram.com/accounts/login')
#         self.browser.implicitly_wait(180)
#
#         #Checking if the page is the login page
#         isNotLoggedIn = "Login" in str((self.browser.title).encode('utf-8').strip())
#         if(isNotLoggedIn):
#             #Filling the inputs
#             self.browser.find_element_by_xpath("//input[@name='username']").send_keys(self.email)
#             self.browser.find_element_by_xpath("//input[@name='password']").send_keys(self.password)
#
#             #Logging in
#             logInButton = self.browser.find_element_by_xpath("//button[contains(.,'Log in')]")
#             logInButton.click()
#             time.sleep(5)
#
#         self.loggedInBrowser = True
#
#     def apiSignIn(self):
#         #Logging into the API
#         self.api = InstagramAPI(self.email, self.password)
#         response = self.api.login()
#         time.sleep(5)
#
#         if(str(response) is "None"):
#             self.loggedInAPI = False
#         elif(str(response) is "True"):
#             self.loggedInAPI = True
#
#         return(self.loggedInAPI)
#
#     def followWithUsername(self, username):
#         try:
#             #Going to the user's instagram account
#             self.browser.get('https://www.instagram.com/' + username + '/')
#             time.sleep(2)
#             #Finding the follow button & Clicking the button if it's the correct button
#             followButton = self.browser.find_element_by_css_selector('button')
#             if (followButton.text != 'Following'):
#                 followButton.click()
#                 time.sleep(2)
#                 return True
#             else:
#                 return False
#         except Exception as e:
#             return(str(e))
#
#     def unfollowWithUsername(self, username):
#         #Going to the user's instagram account
#         self.browser.get('https://www.instagram.com/' + username + '/')
#         time.sleep(2)
#         #Finding the 'Following' button & Clicking the button if it's the correct button
#         followButton = self.browser.find_element_by_css_selector('button')
#         if (followButton.text == 'Following'):
#             followButton.click()
#             time.sleep(2)
#             #Waiting for the prompt to open, then clicking the confirm unfollow button
#             confirmButton = self.browser.find_element_by_xpath('//button[text() = "Unfollow"]')
#             confirmButton.click()
#             return True
#         else:
#             return False
#
#     def unfollowWithAPI(self, userID):
#         #Unfollowing a specified user by UserID
#         self.api.unfollow(userID)
#         return True
#
#     def followWithAPI(self, userID):
#         #Unfollowing a specified user by UserID
#         self.api.follow(userID)
#         return True
#
#     def getFollowing(self):
#         #Getting the followers from the API & Returning them
#         followers = self.api.getTotalFollowings(self.api.username_id)
#         return followers
#
#     def getFollowed(self):
#         #Getting the followers from the API & Returning them
#         followers = self.api.getTotalFollowers(self.api.username_id)
#         return followers
#
#     def followAction(self, listToFollow):
#         #Initializing a counter
#         count = 0
#         #Traversing the list of users
#         for user in listToFollow:
#             #Getting the current user's username
#             username = str(user['Username'])
#             userID = str(user['UserID'])
#
#             if(FOLLOW_WITH_API):
#                 if(self.followWithAPI(userID)):
#                     #Updating the user in the database so that we don't follow them again
#                     post_db_target("UPDATE `tUsersToFollow` SET `HasFollowed` = 1 WHERE `UserID` = '" + str(user['UserID']) + "'", DATABASE)
#                     #Incrementing the current count
#                     count += 1
#             else:
#                 if(self.followWithUsername(username)):
#                     #Updating the user in the database so that we don't follow them again
#                     post_db_target("UPDATE `tUsersToFollow` SET `HasFollowed` = 1 WHERE `UserID` = '" + str(user['UserID']) + "'", DATABASE)
#                     #Incrementing the current count
#                     count += 1
#             #Generating a random time to sleep for
#             randomTime = random.randint(FOLLOW_SLEEP_MIN, FOLLOW_SLEEP_MAX) / 100
#             time.sleep(randomTime)
#
#             #Every X follows, we want to sleep for a little bit
#             if((count % FOLLOW_SLEEP_LONG_FREQUENCY == 0) and (count != 0)):
#                 time.sleep(FOLLOW_SLEEP_LONG / 100)
#
#     def unfollowAction(self, quantity, unfollowAnyone):
#         #Getting the users that I am currently following using the InstagramAPI
#         if(UNFOLLOW_WITH_API):
#             if(unfollowAnyone):
#                 listToUnfollow = query_db_target("SELECT GROUP_CONCAT(userID) FROM tCurrentlyFollowing WHERE (userID NOT IN (SELECT `userID` FROM tWhitelist)) AND (`haveUnfollowed` = 0)", DATABASE)[0]
#             else:
#                 listToUnfollow = query_db_target("SELECT GROUP_CONCAT(userID) FROM tCurrentlyFollowing WHERE (userID NOT IN (SELECT `userID` FROM tWhitelist)) AND (userID NOT IN (SELECT `userID` FROM tCurrentlyFollowed)) AND (`haveUnfollowed` = 0)", DATABASE)[0]
#             if((str(listToUnfollow['GROUP_CONCAT(userID)']) != "None")):
#                 listToUnfollow = listToUnfollow['GROUP_CONCAT(userID)'].split(",")
#             else:
#                 listToUnfollow = []
#         else:
#             if(unfollowAnyone):
#                 listToUnfollow = query_db_target("SELECT GROUP_CONCAT(username) FROM tCurrentlyFollowing WHERE (username NOT IN (SELECT `username` FROM tWhitelist)) AND (`haveUnfollowed` = 0)", DATABASE)[0]
#             else:
#                 listToUnfollow = query_db_target("SELECT GROUP_CONCAT(username) FROM tCurrentlyFollowing WHERE (username NOT IN (SELECT `username` FROM tWhitelist)) AND (username NOT IN (SELECT `username` FROM tCurrentlyFollowed)) AND (`haveUnfollowed` = 0)", DATABASE)[0]
#             if((str(listToUnfollow['GROUP_CONCAT(username)']) != "None")):
#                 listToUnfollow = listToUnfollow['GROUP_CONCAT(username)'].split(",")
#             else:
#                 listToUnfollow = []
#
#         #Initializing a counter
#         count = 0
#         #Traversing the list of users
#         for user in listToUnfollow:
#             #When the current count == quantity we want to stop unfollowing users
#             if(count == quantity):
#                 break
#             #Getting the current user's userID & username
#             # userID = str(user['pk'])
#             # username = str(user['username'])
#
#             if(UNFOLLOW_WITH_API):
#                 if(self.unfollowWithAPI(user)):
#                     post_db_target("UPDATE `tCurrentlyFollowing` SET `haveUnfollowed` = 1 WHERE `userID` = '" + str(user) + "'", DATABASE)
#                     #Incrementing the current count
#                     count += 1
#             else:
#                 if(self.unfollowWithUsername(user)):
#                     post_db_target("UPDATE `tCurrentlyFollowing` SET `haveUnfollowed` = 1 WHERE `username` = '" + str(user) + "'", DATABASE)
#                     #Incrementing the current count
#                     count += 1
#
#             #Generating a random time to sleep for
#             randomTime = random.randint(FOLLOW_SLEEP_MIN, FOLLOW_SLEEP_MAX) / 100
#             time.sleep(randomTime)
#
#             #Every X follows, we want to sleep for a little bit
#             if((count % FOLLOW_SLEEP_LONG_FREQUENCY == 0) and (count != 0)):
#                 time.sleep(FOLLOW_SLEEP_LONG / 100)
#
#     def postImage(self, imageFilename, caption, hashtagArray):
#         try:
#             caption = caption + "\n"
#             for hashtag in hashtagArray:
#                 caption = caption + "#" + hashtag + " "
#
#             # caption = caption + "\n#sunset #sunsetlovers #sunsets #nature #sky #ig #photooftheday #picoftheday #sunrise #sunrisephotography #greatlandscapes_oftheworld #landscapelovers #sunset_captures #landscape_capture #sunsetlover #landscapephotography #landscapelover #bestplaces #landscape_collection #sunsetphotography #landscape_specialist #sunset_stream #sunsetchaser #gf_skies #satisfyingsunsets"
#             response = self.api.uploadPhoto(imageFilename, caption=caption)
#             if(response):
#                 response = "Success"
#             return(str(response))
#         except Exception as e:
#             return(str(e))
#
#     def lookUpUser(self, username):
#         try:
#             self.api.searchUsername(username)
#             username_id = self.api.LastJson["user"]["pk"]
#             return(True, str(username_id))
#         except Exception as e:
#             return(False, str(e))
#
#     def closeBrowser(self):
#         if(self.loggedInBrowser):
#             self.browser.close()
#
#     def __exit__(self, exc_type, exc_value, traceback):
#         self.closeBrowser()
#
#
# STATIC_INSTAGRAM_BOT = InstagramBot(EMAIL, PASSWORD)
# STATIC_INSTAGRAM_BOT.apiSignIn()
# # STATIC_INSTAGRAM_BOT.signIn()
# lastSignInTime = time.time()
#
# ####################### Functions and Endpoints for Handling Images #########################
#
# #Grabbing the raw HTML for a specified URL
# def retrieveWebPageHTML(Url):
#     user_agents=['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20130406 Firefox/23.0',
#                            'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0',
#                            'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533+ \(KHTML, like Gecko) Element Browser 5.0',
#                            'IBM WebExplorer /v0.94', 'Galaxy/1.0 [en] (Mac OS X 10.5.6; U; en)',
#                            'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
#                            'Opera/9.80 (Windows NT 6.0) Presto/2.12.388 Version/12.14',
#                            'Mozilla/5.0 (iPad; CPU OS 6_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) \Version/6.0 Mobile/10A5355d Safari/8536.25',
#                            'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) \Chrome/28.0.1468.0 Safari/537.36',
#                            'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0; TheWorld)']
#     headers={'User-Agent':user_agents,}
#     #Assembling the request which we will make the the specified url
#     request=urllib2.Request(Url,None,headers)
#     #Making the request, and returning the response
#     response = urllib2.urlopen(request).read()
#     return(response)
#
# #Given an HTML string, return all the images found inside the HTML
# def parseHTML(html):
#     soup = BeautifulSoup(html,'html.parser')
#     return(soup.findAll('img', class_="photo-item__img"))
#
# #Given a list of images, filter out profile_pictures/icons/etc
# def refineImageURLS(imgList):
#     properURLS = []
#     for img in imgList:
#         img = img.get('src')
#         #We want to filter out anything that is considered an "asset"
#         if('assets' not in img.split("/")):
#             #Appending the raw url, removing the filters from the end
#             properURLS.append(img.split("?")[0])
#     return properURLS
#
# #Downloading an image and storing it locally
# def downloadFile(ImageURL):
#     #Retrieving the HTML from the Url
#     image = retrieveWebPageHTML(ImageURL)
#     #Grabbing the extension from the original url so that we don't change the type of file
#     extension = ImageURL.split(".")[len(ImageURL.split("."))-1]
#     #Creating the filename where we will store the image
#     imageFilename = "/var/www/FlaskApp/FlaskApp/RecentImage" + "." + extension
#     #Writing the image
#     output = open(imageFilename,"wb")
#     output.write(image)
#     output.close()
#     return(imageFilename)
#
# #The endpoint which will be used to grab all the potential image urls
# @app.route("/ENDPOINTS/getImagesToPost/", methods=["GET"])
# def getImagesToPost():
#     try:
#         limit = request.args.get('limit');
#         if(limit is None):
#             #Constructing a Response
#             response = jsonify([])
#             response.status_code = 200
#             return(response)
#         else:
#             limit = int(limit)
#             #Getting the list of urls that we have previously posted
#             usedImages =  query_db_target("SELECT GROUP_CONCAT(imageURL) FROM tUsedImages", DATABASE)[0]
#             if((str(usedImages['GROUP_CONCAT(imageURL)']) != "None")):
#                 usedImages = usedImages['GROUP_CONCAT(imageURL)'].split(",")
#             else:
#                 usedImages = []
#
#             #Getting the list of urls that we marked as unwanted
#             unwantedImages =  query_db_target("SELECT GROUP_CONCAT(imageURL) FROM tUnwantedImages", DATABASE)[0]
#             if((str(unwantedImages['GROUP_CONCAT(imageURL)']) != "None")):
#                 unwantedImages = unwantedImages['GROUP_CONCAT(imageURL)'].split(",")
#             else:
#                 unwantedImages = []
#
#             imageArray = []
#             pageCount = FIRST_IMAGE_PAGE
#             imageCounter = 0
#             while(True):
#                 PEXELS_URL = "https://www.pexels.com/search/sunset/?page=" + str(pageCount)
#                 #Getting the raw HTML from the specified url
#                 pexelsHTML = retrieveWebPageHTML(PEXELS_URL)
#                 #Getting all the images from the HTML we previously queried for.
#                 parsedHTMLImgs = parseHTML(pexelsHTML)
#                 #Refining the Img URLS
#                 parsedHTMLImgs = refineImageURLS(parsedHTMLImgs)
#                 for img in parsedHTMLImgs:
#                     #Checking to see if we might want to use this image
#                     if((img not in usedImages) and (img not in unwantedImages)):
#                         #Appending the image if its valid
#                         imageArray.append(img)
#                         imageCounter += 1
#                         if(imageCounter >= limit):
#                             #Constructing a Response
#                             response = jsonify(imageArray)
#                             response.status_code = 200
#                             return(response)
#                 pageCount += 1
#             #Constructing a Response
#             response = jsonify(imageArray)
#             response.status_code = 200
#             return(response)
#     except Exception as e:
#         #Constructing a Response
#         data = str(e)
#         response = jsonify(data)
#         response.status_code = 200
#         return(response)
#
# #The endpoint which will initialize the IGBot and post an image given a specified URL and Caption
# @app.route("/ENDPOINTS/postImage/", methods=["POST"])
# def postImage():
#     try:
#         global STATIC_INSTAGRAM_BOT
#         global lastSignInTime
#
#         isSuccessful, userID = STATIC_INSTAGRAM_BOT.lookUpUser("instagram")
#         if(not isSuccessful):
#             # STATIC_INSTAGRAM_BOT.closeBrowser()
#             # STATIC_INSTAGRAM_BOT = InstagramBot(EMAIL, PASSWORD)
#             STATIC_INSTAGRAM_BOT.apiSignIn()
#             # STATIC_INSTAGRAM_BOT.signIn()
#             lastSignInTime = time.time()
#
#         #Grabbing the ImageURL & Caption for the post
#         ImageURL = str(request.form['URL'])
#         Caption = str(request.form['Caption'])
#         # ImageURL = "https://images.pexels.com/photos/36717/amazing-animal-beautiful-beautifull.jpg"
#         # Caption = "What's meant to be will always find a way - Trisha Yearwood"
#
#         #Downloading the image and storing the directory of the image in imageFilename
#         imageFilename = downloadFile(ImageURL)
#
#         #Grabbing the hashtags
#         hashtags =  query_db_target("SELECT GROUP_CONCAT(hashtag) FROM tHashtags", DATABASE)[0]
#         if((str(hashtags['GROUP_CONCAT(hashtag)']) != "None")):
#             hashtags = hashtags['GROUP_CONCAT(hashtag)'].split(",")
#         else:
#             hashtags = []
#
#         #Posting the image with the caption & set of hashtags we want to append
#         response = STATIC_INSTAGRAM_BOT.postImage(imageFilename, Caption, hashtags)
#
#         #Removing the image from our directory
#         os.remove(imageFilename)
#
#         if(response == "Success"):
#             #Adding the ImageURL to our database
#             values = (ImageURL, time.time())
#             post_db_target("INSERT INTO tUsedImages (imageURL, time) VALUES (?, ?)", DATABASE, values)
#
#         #Constructing a response
#         data = {"Response":str(response)}
#         response = jsonify(data)
#         response.status_code = 200
#         return(response)
#     except Exception as e:
#         #Constructing a response
#         data = {"Response":str(e)}
#         response = jsonify(data)
#         response.status_code = 200
#         return(response)
#
# #Adding an ImageURL to the list of Unwanted Images so that we don't reuse these images
# @app.route("/ENDPOINTS/addUnwantedImage/", methods=["POST"])
# def addUnwantedImage():
#     try:
#         #Grabbing the URL from the arguments
#         ImageURL = str(request.form['URL'])
#
#         #Adding the ImageURL to our database
#         values = (ImageURL, time.time())
#         post_db_target("INSERT INTO tUnwantedImages (imageURL, time) VALUES (?, ?)", DATABASE, values)
#
#         data = {"Response":"Success"}
#         response = jsonify(data)
#         response.status_code = 200
#         return(response)
#     except Exception as e:
#         data = {"Response":str(e)}
#         response = jsonify(data)
#         response.status_code = 200
#         return(response)
#
# #Removing an ImageURL from the list of Unwanted Images so that we will be able to post this image again
# @app.route("/ENDPOINTS/removeUnwantedImage/", methods=["POST"])
# def removeUnwantedImage():
#     try:
#         #Grabbing the URL from the arguments
#         ImageURL = str(request.form['URL'])
#
#         #Deleting the ImageURL to our database
#         post_db_target("DELETE FROM tUnwantedImages WHERE imageURL = '" + str(ImageURL) + "'", DATABASE)
#
#         data = {"Response":"Success"}
#         response = jsonify(data)
#         response.status_code = 200
#         return(response)
#     except Exception as e:
#         data = {"Response":str(e)}
#         response = jsonify(data)
#         response.status_code = 200
#         return(response)
#
# #############################################################################################
#
# #-------------------------------------------------------------------------------------------#
#
# #################### Functions and Endpoints for Unfollowing Accounts #######################
#
# #The thread which will Initialize the IGBot to unfollow accounts
# def unfollowingThread(Quantity, UnfollowAnyone, IGBot):
#     try:
#         #Calculating the amount of time it will take to follow this many users(May be less than quantity)
#         followingTime = ((FOLLOW_SLEEP_MAX / 100) * Quantity) + (int(Quantity / FOLLOW_SLEEP_LONG_FREQUENCY) * (FOLLOW_SLEEP_LONG / 100))
#
#         #Calculating the time which the following process will be done.
#         currentTime = int(time.time())
#         values = "Unfollow", Quantity, currentTime, (currentTime + followingTime)
#         post_db_target("INSERT INTO tActions (action, quantity, beginTime, endTime) VALUES (?, ?, ?, ?)", DATABASE, values)
#
#         #Telling the Instagram Bot to follow everyone in the list
#         IGBot.unfollowAction(Quantity, UnfollowAnyone)
#     except Exception as e:
#         #Emailing myself about the error
#         return(str(e))
#
# #The endpoint which will be used to indicate how many people to unfollow
# @app.route("/ENDPOINTS/unfollowUsers/", methods=["POST"])
# def unfollow():
#     try:
#         #Getting the current time
#         currentTime = int(time.time())
#
#         #Checking if there is an action that will end later than the current time
#         allActions = query_db_target("SELECT * FROM tActions WHERE `endTime` > '" + str(currentTime) + "'", DATABASE)
#         if(len(allActions) == 0):
#             Quantity = None
#             if(request.method == "GET"):
#                 Quantity = int(request.args.get('Quantity'))
#             elif(request.method == "POST"):
#                 Quantity = int(request.form['Quantity'])
#             if(Quantity is None):
#                 #Constructing a response
#                 data = {'Response' : "No Arguments"}
#                 response = jsonify(data)
#                 response.status_code = 200
#                 return(response)
#
#             UnfollowAnyone = None
#             if(request.method == "GET"):
#                 UnfollowAnyone = (str(request.args.get("UnfollowAnyone")) == "true")
#             elif(request.method == "POST"):
#                 UnfollowAnyone = (str(request.form["UnfollowAnyone"]) == "true")
#             if(UnfollowAnyone is None):
#                 #Constructing a response
#                 data = {'Response' : "No Arguments"}
#                 response = jsonify(data)
#                 response.status_code = 200
#                 return(response)
#
#             # #Creating a InstagramBot and logging in
#             # IGBot = InstagramBot(EMAIL, PASSWORD)
#             # if(UNFOLLOW_WITH_API):
#             #     isSignedIn = IGBot.apiSignIn()
#             #     if(not isSignedIn):
#             #         #Constructing a response
#             #         data = {"Response":"Instagram Bot not signed in!"}
#             #         response = jsonify(data)
#             #         response.status_code = 200
#             #         return(response)
#             # else:
#             #     IGBot.signIn()
#             global STATIC_INSTAGRAM_BOT
#             global lastSignInTime
#
#             isSuccessful, userID = STATIC_INSTAGRAM_BOT.lookUpUser("instagram")
#             if(not isSuccessful):
#                 # STATIC_INSTAGRAM_BOT.closeBrowser()
#                 # STATIC_INSTAGRAM_BOT = InstagramBot(EMAIL, PASSWORD)
#                 STATIC_INSTAGRAM_BOT.apiSignIn()
#                 # STATIC_INSTAGRAM_BOT.signIn()
#                 lastSignInTime = time.time()
#
#             #If we are not currently performing any actions(Following/Unfollowing/Posting) then we want to proceed with this by starting the followingThread
#             thread = threading.Thread(target=unfollowingThread, args=(Quantity, UnfollowAnyone, STATIC_INSTAGRAM_BOT,), name='unfollowingThread')
#             thread.start()
#             # return(str(unfollowingThread(Quantity, IGBot)))
#
#             #Constructing a response
#             data = {'Response' : "Success"}
#             response = jsonify(data)
#             response.status_code = 200
#             return(response)
#         else:
#             #Constructing a response
#             data = {'Response' : "Currently Following/Unfollowing People"}
#             response = jsonify(data)
#             response.status_code = 200
#             return(response)
#     except Exception as e:
#         #Need to email myself about the error
#         #Constructing a response
#         data = {'Response' : str(e)}
#         response = jsonify(data)
#         response.status_code = 200
#         return(response)
#
# #############################################################################################
#
# #-------------------------------------------------------------------------------------------#
#
# #################### Functions and Endpoints for Following Accounts #########################
#
# #The thread which will Initialize the IGBot to follow accounts
# def followingThread(Quantity, IGBot):
#     try:
#         #Grabbing a list of people to follow from the database with the max = quantity
#         listToFollow = query_db_target("SELECT * FROM `tUsersToFollow` WHERE `HasFollowed` = 0 LIMIT " + str(Quantity), DATABASE)
#
#         #Calculating the amount of time it will take to follow this many users(May be less than quantity)
#         followingTime = ((FOLLOW_SLEEP_MAX / 100) * len(listToFollow)) + (int(len(listToFollow) / FOLLOW_SLEEP_LONG_FREQUENCY) * (FOLLOW_SLEEP_LONG / 100))
#
#         #Calculating the time which the following process will be done.
#         currentTime = int(time.time())
#         values = "Follow", Quantity, currentTime, (currentTime + followingTime)
#         post_db_target("INSERT INTO tActions (action, quantity, beginTime, endTime) VALUES (?, ?, ?, ?)", DATABASE, values)
#
#         #Telling the Instagram Bot to follow everyone in the list
#         IGBot.followAction(listToFollow)
#     except Exception as e:
#         #Emailing myself about the error
#         return(str(e))
#
# #The endpoint which will be used to indicate how many people to follow
# @app.route("/ENDPOINTS/followUsers/", methods=["GET"])
# def follow():
#     try:
#         #Getting the current time
#         currentTime = int(time.time())
#
#         #Checking if there is an action that will end later than the current time
#         allActions = query_db_target("SELECT * FROM tActions WHERE `endTime` > '" + str(currentTime) + "'", DATABASE)
#         if(len(allActions) == 0):
#             Quantity = None
#             if(request.method == "GET"):
#                 Quantity = int(request.args.get('Quantity'))
#             elif(request.method == "POST"):
#                 Quantity = int(request.form['Quantity'])
#             if(Quantity is None):
#                 #Constructing a response
#                 data = {'Response' : "No Arguments"}
#                 response = jsonify(data)
#                 response.status_code = 200
#                 return(response)
#
#             global STATIC_INSTAGRAM_BOT
#             global lastSignInTime
#
#             isSuccessful, userID = STATIC_INSTAGRAM_BOT.lookUpUser("instagram")
#             if(not isSuccessful):
#                 # STATIC_INSTAGRAM_BOT.closeBrowser()
#                 # STATIC_INSTAGRAM_BOT = InstagramBot(EMAIL, PASSWORD)
#                 STATIC_INSTAGRAM_BOT.apiSignIn()
#                 # STATIC_INSTAGRAM_BOT.signIn()
#                 lastSignInTime = time.time()
#
#             #If we are not currently performing any actions(Following/Unfollowing/Posting) then we want to proceed with this by starting the followingThread
#             thread = threading.Thread(target=followingThread, args=(Quantity, STATIC_INSTAGRAM_BOT,), name='followingThread')
#             thread.start()
#
#             #Constructing a response
#             data = {'Response' : "Done following " + str(Quantity) + " people."}
#             response = jsonify(data)
#             response.status_code = 200
#             return(response)
#         else:
#             #Constructing a response
#             data = {'Response' : "Currently Following/Unfollowing People"}
#             response = jsonify(data)
#             response.status_code = 200
#             return(response)
#     except Exception as e:
#         #Need to email myself about the error
#         #Constructing a response
#         data = {'Response' : str(e)}
#         response = jsonify(data)
#         response.status_code = 200
#         return(response)
#
# #The endpoint which will update the list of users in the tUsersToFollow table
# @app.route("/ENDPOINTS/updateUsersToFollow/", methods=["GET"])
# def updateUsersToFollow():
#     return("Testing")
#
# #############################################################################################
#
# # Updates the list of users to unfollow based on my current following
# @app.route("/ENDPOINTS/updateFollowInformation/", methods=["GET"])
# def updateUserFollowing():
#     try:
#         global STATIC_INSTAGRAM_BOT
#         global lastSignInTime
#
#         isSuccessful, userID = STATIC_INSTAGRAM_BOT.lookUpUser("instagram")
#         if(not isSuccessful):
#             # STATIC_INSTAGRAM_BOT.closeBrowser()
#             # STATIC_INSTAGRAM_BOT = InstagramBot(EMAIL, PASSWORD)
#             STATIC_INSTAGRAM_BOT.apiSignIn()
#             # STATIC_INSTAGRAM_BOT.signIn()
#             lastSignInTime = time.time()
#
#         following = STATIC_INSTAGRAM_BOT.getFollowing()
#         post_db_target("DELETE FROM tCurrentlyFollowing", DATABASE)
#         for user in following:
#             values = (user['username'], user['pk'])
#             post_db_target("INSERT INTO tCurrentlyFollowing (username, userID) VALUES (?, ?)", DATABASE, values)
#         followed = STATIC_INSTAGRAM_BOT.getFollowed()
#         post_db_target("DELETE FROM tCurrentlyFollowed", DATABASE)
#         for user in followed:
#             values = (user['username'], user['pk'])
#             post_db_target("INSERT INTO tCurrentlyFollowed (username, userID) VALUES (?, ?)", DATABASE, values)
#         return("Success")
#     except Exception as e:
#         return(str(e))
#
# # Updates the list of users to unfollow based on my current following
# @app.route("/ENDPOINTS/checkCode/", methods=["GET"])
# def checkCode():
#     try:
#         # listToUnfollow = query_db_target("SELECT GROUP_CONCAT(userID) FROM tCurrentlyFollowing WHERE (userID NOT IN (SELECT `userID` FROM tWhitelist)) AND (`haveUnfollowed` = 0)", DATABASE)[0]
#         # listToUnfollow = query_db_target("SELECT GROUP_CONCAT(userID) FROM tCurrentlyFollowing WHERE (userID NOT IN (SELECT `userID` FROM tWhitelist)) AND (userID NOT IN (SELECT `userID` FROM tCurrentlyFollowed)) AND (`haveUnfollowed` = 0)", DATABASE)[0]
#         listToUnfollow = query_db_target("SELECT GROUP_CONCAT(userID) FROM tCurrentlyFollowing WHERE (userID IN (SELECT `userID` FROM tCurrentlyFollowed)) AND (`haveUnfollowed` = 0)", DATABASE)[0]
#         if((str(listToUnfollow['GROUP_CONCAT(userID)']) != "None")):
#             listToUnfollow = listToUnfollow['GROUP_CONCAT(userID)'].split(",")
#         else:
#             listToUnfollow = []
#         return(str(len(listToUnfollow)))
#     except Exception as e:
#         return(str(e))
#
#
# # Updates the list of users to unfollow based on my current following
# @app.route("/ENDPOINTS/getWhiteList/", methods=["GET"])
# def getWhiteList():
#     try:
#         whitelist = query_db_target("SELECT `username`,`userID` FROM tWhitelist", DATABASE)
#         response = jsonify(whitelist)
#         response.status_code = 200
#         return(response)
#     except Exception as e:
#         data = {"Response":str(e)}
#         response = jsonify(data)
#         response.status_code = 200
#         return(response)
#
# # Updates the list of users to unfollow based on my current following
# @app.route("/ENDPOINTS/addToWhiteList/", methods=["POST"])
# def addToWhiteList():
#     try:
#         username = str(request.form['username'])
#
#         global STATIC_INSTAGRAM_BOT
#         global lastSignInTime
#
#         isSuccessful, userID = STATIC_INSTAGRAM_BOT.lookUpUser("instagram")
#         if(not isSuccessful):
#             # STATIC_INSTAGRAM_BOT.closeBrowser()
#             # STATIC_INSTAGRAM_BOT = InstagramBot(EMAIL, PASSWORD)
#             STATIC_INSTAGRAM_BOT.apiSignIn()
#             # STATIC_INSTAGRAM_BOT.signIn()
#             lastSignInTime = time.time()
#
#         isSuccessful, userID = STATIC_INSTAGRAM_BOT.lookUpUser(username)
#
#         if(isSuccessful):
#             values = (username, str(userID))
#             post_db_target("INSERT INTO tWhitelist (username, userID) VALUES (?, ?)", DATABASE, values)
#
#             data = {"Response":str(userID)}
#             response = jsonify(data)
#             response.status_code = 200
#             return(response)
#         else:
#             data = {"Response":"Failure - " + str(userID)}
#             response = jsonify(data)
#             response.status_code = 200
#             return(response)
#     except Exception as e:
#         data = {"Response":str(e)}
#         response = jsonify(data)
#         response.status_code = 200
#         return(response)
#
# # Updates the list of users to unfollow based on my current following
# @app.route("/ENDPOINTS/removeFromWhiteList/", methods=["POST"])
# def removeFromWhiteList():
#     try:
#         userID = str(request.form['userID'])
#         post_db_target("DELETE FROM tWhitelist WHERE userID=" + userID, DATABASE)
#         data = {"Response":"Success"}
#         response = jsonify(data)
#         response.status_code = 200
#         return(response)
#     except Exception as e:
#         data = {"Response":str(e)}
#         response = jsonify(data)
#         response.status_code = 200
#         return(response)
#
# # Updates the list of users to unfollow based on my current following
# @app.route("/ENDPOINTS/login/", methods=["GET"])
# def reLogin():
#     try:
#         isSuccessful, userID = STATIC_INSTAGRAM_BOT.lookUpUser("instagram")
#         if(isSuccessful):
#             data = {"Response":"Success"}
#             response = jsonify(data)
#             response.status_code = 200
#             return(response)
#         else:
#             global STATIC_INSTAGRAM_BOT
#             global lastSignInTime
#
#             # STATIC_INSTAGRAM_BOT.closeBrowser()
#             # STATIC_INSTAGRAM_BOT = InstagramBot(EMAIL, PASSWORD)
#             STATIC_INSTAGRAM_BOT.apiSignIn()
#             # STATIC_INSTAGRAM_BOT.signIn()
#             lastSignInTime = time.time()
#
#             data = {"Response":"Logged In Successfully"}
#             response = jsonify(data)
#             response.status_code = 200
#             return(response)
#     except Exception as e:
#         data = {"Response":str(e)}
#         response = jsonify(data)
#         response.status_code = 200
#         return(response)
#
# # Updates the list of users to unfollow based on my current following
# @app.route("/ENDPOINTS/getHashtags/", methods=["GET"])
# def getHashtagsh():
#     try:
#         hashtags = query_db_target("SELECT `hashtag` FROM tHashtags", DATABASE)
#         response = jsonify(hashtags)
#         response.status_code = 200
#         return(response)
#     except Exception as e:
#         data = {"Response":str(e)}
#         response = jsonify(data)
#         response.status_code = 200
#         return(response)
#
# # Updates the list of users to unfollow based on my current following
# @app.route("/ENDPOINTS/removeHashtag/", methods=["POST"])
# def removeHashtag():
#     try:
#         hashtag = str(request.form['hashtag'])
#
#         post_db_target("DELETE FROM tHashtags WHERE `hashtag`='" + hashtag + "'", DATABASE)
#         data = {"Response":"Success"}
#         response = jsonify(data)
#         response.status_code = 200
#         return(response)
#     except Exception as e:
#         data = {"Response":str(e)}
#         response = jsonify(data)
#         response.status_code = 200
#         return(response)
#
# # Updates the list of users to unfollow based on my current following
# @app.route("/ENDPOINTS/addHashtag/", methods=["POST"])
# def addHashtag():
#     try:
#         hashtag = str(request.form['hashtag'])
#
#         values = (hashtag,)
#         post_db_target("INSERT INTO tHashtags (hashtag) VALUES (?)", DATABASE, values)
#
#         data = {"Response":"Success"}
#         response = jsonify(data)
#         response.status_code = 200
#         return(response)
#     except Exception as e:
#         data = {"Response":str(e)}
#         response = jsonify(data)
#         response.status_code = 200
#         return(response)
