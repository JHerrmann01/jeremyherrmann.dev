from InstagramAPI import InstagramAPI
import credentials

def load_information():
    return credentials.username, credentials.password

def login():
    #Acquiring the username and password
    username, password = load_information()
    #Creating the Instagram User from the stored credentials
    API = InstagramAPI(username, password)
    #Logging the User into Instagram and checking the response
    if(API.login()):
        #If we were able to log the user in, we will display a message and then return the API object
        print("Successfully logged the user in!")
        return(API)
    else:
        #If we weren't able to log the user in, we will display an error message and exit the application
        print("Unable to log the user in!")
        exit(1)
    return(None)

def logout(API):
    print("Logging the user out!")
    #Logging out the User
    API.logout()
    #Successfully exiting the program
    exit(0)
