#!/usr/bin/python
import load_information as load_info
import database_functions as DB
from InstagramAPI import InstagramAPI
import time, random

def getTotalFollowers(api, user_id):
    """
    Returns the list of followers of the user.
    It should be equivalent of calling api.getTotalFollowers from InstagramAPI
    """

    followers = []
    next_max_id = True
    while next_max_id:
        # first iteration hack
        if next_max_id is True:
            next_max_id = ''

        _ = api.getUserFollowers(user_id, maxid=next_max_id)
        followers.extend(api.LastJson.get('users', []))
        next_max_id = api.LastJson.get('next_max_id', '')

    follower_pk = []
    for follower in followers:
        follower_pk.append(follower['pk'])
    return follower_pk

def unfollow_users(API):
    # List of all followers
    follower_list = getTotalFollowers(API, API.username_id)
    #Getting a random number of people to begin unfollowing
    QUANTITY_TO_UNFOLLOW = random.randint(250, 350)
    print("Unfollowing " + str(QUANTITY_TO_UNFOLLOW))
    #Getting the current list of users I am following
    following = API.getTotalFollowings(API.username_id)
    refinedList = []
    for user in following:
        if(user['pk'] not in follower_list):
            refinedList.append(user)
    print("Number of people we follow but dont follow back: " + str(len(refinedList)))

    #Printing out information about accounts I'm following
    print("Currently following: " + str(len(following)))
    #Fixing the QUANTITY_TO_UNFOLLOW in case it's larger than the amount of people I follow
    if(QUANTITY_TO_UNFOLLOW > len(refinedList)):
        QUANTITY_TO_UNFOLLOW = len(refinedList)
    #Traversing from 0 -> QUANTITY_TO_UNFOLLOW
    for i in range(0, QUANTITY_TO_UNFOLLOW):
        #Getting a random index
        unfollow_index = random.randint(0, len(refinedList))
        '''
        while(following[unfollow_index]['pk'] in follower_list):
            try:
                print("Don't unfollow this account, they are following us! - " + str(following[unfollow_index]))
            except Exception as e:
                print("Error printing follower name: " + str(e))
            unfollow_index = random.randint(0, len(following))
        '''
        try:
            print("Unfollowing: " + str(refinedList[unfollow_index]) + "\n\n")
        except Exception as e:
            print("Error printing name: " + str(e))
        #Unfollowing the user at the unfollow_index
        API.unfollow(refinedList[unfollow_index]['pk'])
        #Sleeping for a random time between 15-20 seconds
        time.sleep(random.randint(1500, 2000) / 100)
        #Every 10 people we will sleep for 10 seconds
        if((i != 0) and (i % 10 == 0)):
            print("Sleeping for 20 seconds!")
            time.sleep(20)

if(__name__ == "__main__"):
    #Printing some debug statements.
    print("BEGINNING INSTAGRAM FOLLOW APPLICATION\n" + str(time.time()))

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
    unfollow_users(Instagram_API)

    #Logging the user out
    print("LOGGING OUT OF THE INSTAGRAM API")
    load_info.logout(Instagram_API)
