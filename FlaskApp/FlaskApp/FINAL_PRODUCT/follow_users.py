#!/usr/bin/python
import load_information as load_info
import database_functions as DB
from InstagramAPI import InstagramAPI
import time, random

def follow_users(API):
    print("ENTERING THE follow_users() function")
    #Getting a random amount of people that we will begin following
    QUANTITY_TO_FOLLOW = random.randint(290, 410)
    print("FOLLOWING " + str(QUANTITY_TO_FOLLOW) + " USERS")
    #Getting the list of people we will follow
    list_to_follow = DB.get_random_follow_list(QUANTITY_TO_FOLLOW)
    #Traversing the list of people to follow
    for i in range(0, len(list_to_follow)):
        try:
            print("FOLLOWING: " + str(list_to_follow[i]))
            #Getting the current user
            user = list_to_follow[i]
            #Following the current user with the API
            API.follow(user['UserID'])
            #Setting the status of the current user in the DB
            DB.update_has_followed(user['UserID'])
            #Sleeping for a random time between 15-20 seconds
            time.sleep(random.randint(1500, 2000) / 100)
            #Every 10 people we will sleep for 10 seconds
            if((i != 0) and (i % 10 == 0)):
                print("Sleeping for 20 seconds!")
                time.sleep(20)
        except Exception as error:
            print("Error: " + str(error))

if(__name__ == "__main__"):
    #Printing some debug statements.
    print("BEGINNING INSTAGRAM FOLLOW APPLICATION\n")

    #Sleeping for a random time between 0 - 30 minutes
    MINUTES_TO_SLEEP = random.randint(0, 30)
    print("SLEEPING FOR " + str(MINUTES_TO_SLEEP) + " MINUTES BEFORE FOLLOWING USERS")
    time.sleep(MINUTES_TO_SLEEP * 60)

    #Making the Instagram API and logging in the user
    print("LOGGING INTO THE INSTAGRAM API")
    Instagram_API = load_info.login()
    print("LOGGED IN - SLEEPING FOR 5 MINUTES")
    time.sleep(5*60)

    #Calling the follow_users function
    follow_users(Instagram_API)
    
    #Logging the user out
    print("LOGGING OUT OF THE INSTAGRAM API")
    load_info.logout(Instagram_API)
