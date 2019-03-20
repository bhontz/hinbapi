from flask import Flask, request
from PIL import Image
from math import ceil
import sys, requests, json
from io import BytesIO
from datetime import datetime

app = Flask(__name__)

def log(msg):  # simple wrapper for logging to stdout on heroku
    try:
        if type(msg) is dict:
            msg = json.dumps(msg)
        else:
            msg = str(msg, 'utf-8')
        sys.stdout.write(u"{}: {}".format(datetime.now(), msg))
    except UnicodeEncodeError:
        pass  # squash logging errors in case of non-ascii text
    sys.stdout.flush()

def AzumioFormat(strURL, strPathfilenameOut):
    """
    Takes a URL of an image file and formats it to the 544x544 size required by the Azumio API
    :param strURL: url of image file
    :param strPathfilenameOut: File that is written in Azumio's required format (and Azumio's API requires a file, not a URL)
    :return:
    """
    r = True

    try:
        response = requests.get(strURL)
        im = Image.open(BytesIO(response.content))
    except(IOError) as detail:
        log("I/O Error: {}".format(detail))
        r = False
    else:
        width, height = im.size

        if (width != height):  # not a square image!
            cw = int(ceil(width / 2.0))
            ch = int(ceil(height / 2.0))
            if ch > cw:
                fromtop = ch - cw
                crop_rectangle = (0, fromtop, width, height - fromtop)
            else:
                fromleft = cw - ch
                crop_rectangle = (fromleft, 0, width - fromleft, height)

            im = im.crop(crop_rectangle)

        im = im.resize((544, 544))

        try:
            im.save(strPathfilenameOut)
        except(IOError) as detail:
            log("I/O Error: {}".format(detail))
            r = False

    return(r)

def AzumioJSONparse(response_text):
    """
        Parses the lengthly Azumio response text to something matching their Calorie Mama website illustration
    :param response_text: full response from the Azumio API
    :return: JSON object which should go back to ThunkableX
    looks like: {"Apple": [{"name": "Red Apple", "servingSize": "1 large", "calories": 153}, {"name": "Sliced Apple", "servingSize": "1 slice", "calories": 10}, ... ]}
    """
    obj = json.loads(response_text)

    log(response_text[:64])

    dictReturn = dict()
    # strGroupName = obj["results"][0]["group"]   # these would be different each time, can't parse that on the ThunkableX end!
    strGroupName = "foodItem"
    lstReturn = list()
    for d in obj["results"][0]["items"]:
        dR = dict()
        dR["name"] = d["name"]
        if "unit" in d["servingSizes"][0] and "servingWeight" in d["servingSizes"][0]:  # found that not every item has these!
            dR["servingSize"] = d["servingSizes"][0]["unit"]
            dR["calories"] = round(d["nutrition"]["calories"] * d["servingSizes"][0]["servingWeight"])
            lstReturn.append(dR)

    dictReturn[strGroupName] = lstReturn

    return(json.dumps(dictReturn))


# had to set ThunkableX header to Content-Type:application/x-www-form-urlencoded
# and i could then set the Body using a block to "input=yourstringhere"

# this is how you CURL to the API as a test outside of ThunkableX (i.e. replicating ThunkableX's blocks)
# (and here using a test photo in the Coludinary database)
# curl -H "Content-Type:application/x-www-form-urlencoded" -d "input=https://res.cloudinary.com/dpeqsj31d/image/upload/v1552344323/apple.jpg" http://127.0.0.1:5000
#
# base Azumio post:
# curl -H -i -F media=@image.jpeg https://api-2445582032290.production.gw.apicast.io/v1/foodrecognition?user_key=***REMOVED***


@app.route("/", methods=['POST'])
def listen():
    strImageURL = request.form['input']
    AzumioFormat(strImageURL, 'hinbtemporaryimage.jpg')  # LOCAL USAGE: /users/brad/desktop just a spot on disk for transfer of the image file to the Azumio API

    response = requests.post("https://api-2445582032290.production.gw.apicast.io/v1/foodrecognition?user_key=" + "ACCESS_TOKEN",
                             files={"file": ("media", open('hinbtemporaryimage.jpg', 'rb'), "image/jpeg")})  # LOCAL USAGE: /users/brad/desktop/hinbtemporaryimage.jpg


    return(AzumioJSONparse(response.text))
    
if __name__ == "__main__":
    app.run(debug=True, port=5000)
