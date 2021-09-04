import os
from PIL import Image
def correct_all_images():
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
FROM_DIRECTORY = "/var/www/FlaskApp/FlaskApp/APP/ValidImages/"
TO_DIRECTORY = "/var/www/FlaskApp/FlaskApp/APP/ValidImagesOutput/"

def correct_image(file_name):
    from_file_name = FROM_DIRECTORY + file_name
    file_image = Image.open(from_file_name)
    width, height = file_image.size
    smaller = min(width, height)

    new_width = width * 1080/float(smaller)
    new_height = height * 1080/float(smaller)

    aspect_ratio = new_width / new_height

    if(aspect_ratio <= 1.8 and aspect_ratio >= 0.85):
        print("Width: " + str(new_width) + "Height: " + str(new_height))
        file_image = Image.open(from_file_name)
        file_image.thumbnail((int(new_width), int(new_height)), Image.ANTIALIAS)
        file_image.save(TO_DIRECTORY + file_name, "JPEG")

if(__name__ == "__main__"):
    print("Starting conversion")
    file_list = os.listdir(FROM_DIRECTORY)
    for file_name in file_list:
        print(str(file_name))
        correct_image(file_name)
