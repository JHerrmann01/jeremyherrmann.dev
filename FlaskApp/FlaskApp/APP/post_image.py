import load_information as load_info
import database_functions as DB
from InstagramAPI import InstagramAPI
import time, sys, random, os
from PIL import Image

def post_image(API):
    try:
        #Grabbing all the images from the file
        file_list = os.listdir("/var/www/FlaskApp/FlaskApp/APP/ValidImagesOutput/")
        random_file = file_list[random.randint(0, len(file_list)-1)]
        file_name = "/var/www/FlaskApp/FlaskApp/APP/ValidImagesOutput/"+random_file
        print(file_name)
        '''for tempfile in file_list:
            file_name = "./ValidImages/"+tempfile
            try:
                im = Image.open(file_name)
                im.thumbnail((1024, 1024), Image.ANTIALIAS)
                im.save("./ValidImagesOutput/" + tempfile, "JPEG")
            except IOError as e:
                print(str(e))
                print "cannot create thumbnail for '%s'" % file_name
        '''

        #image_file = open(file_name)
        #print("open file")
        #image = Image.open(image_file)
        #print("assign image")
        ##Stripping the exif data
        #data = list(image.getdata())
        #print("getting data")
        #image_without_exif = Image.new(image.mode, image.size)
        #print("getting image without exif")
        #image_without_exif.putdata(data)
        #print("putting the image")

        #image_without_exif.save(file_name)
        print("saving")
        print("done")
        try:
            print("Inside Try")
            #Grabbing the list of captions from the DB
            all_captions = DB.get_captions()
            print(str(all_captions))
            caption = all_captions[random.randint(0, len(all_captions)-1)]
            caption = str(caption['Caption']) + "\n"
            caption = caption + "\n#sunset #sunsetlovers #sunsets #nature #sky #ig #photooftheday #picoftheday #sunrise #sunrisephotography #greatlandscapes_oftheworld #landscapelovers #sunset_captures #landscape_capture #sunsetlover #landscapephotography #landscapelover #bestplaces #landscape_collection #sunsetphotography #landscape_specialist #sunset_stream #sunsetchaser"
            print(str(caption))
            response = API.uploadPhoto(file_name, caption=caption)
            print(str(response))
            response = API.uploadStoryPhoto(file_name)
            print(str(response))
            print("Successfully uploaded the image!")
            os.remove(file_name)
        except Exception as e:
            print("Error: " + str(e))

    except Exception as e:
        print(str(e))

if(__name__ == "__main__"):
    #Printing some debug statements.
    print("BEGINNING INSTAGRAM APPLICATION\n")

    #Grabbing the current account information
    print("ACQUIRING ACCOUNT INFORMATION & LOGGING IN ACCOUNT")
    Instagram_API = load_info.login()
    time.sleep(5*60)

    #Posting an image
    post_image(Instagram_API)

    print("Logging out!")
    load_info.logout(Instagram_API)
