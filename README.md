**HINBAPI - private API to link ThunkableX to the Azumio API**

This project was created for the 2019 "Health In Bytes" Technovation Challenge team.

This simple API is used as an intermediary between the Azumio food identification API and the ThunkableX phone app building application.

The Azumio API requires posting a image file to the form variable "media".  Further, the image file has a size requirement of 544x544 bytes.

The Thunkable X API does not permit posting files, and the Azumio API won't take the URL of an image.

Consequently, this little API was written to receive the URL of an image from Thunkable X, to center crop and then resize that image, and then to post the resultant image onto the Azumio API.

Since the Azumio API returns more JSON than we'd consider using with the Thunkable X app, this API also filters down the JSON response from the Azumio API before passing it back to the Thunkable X app.

A note regarding calling this API from Thunkable X; I had to set the Thunkable X (in design mode) header argument to Content-Type:application/x-www-form-urlencoded. Within the block coding (i.e. API block), I then set the body to "input=urlOfImage".  I used the form name "input" within this API.

Lastly, I'm using the Heroku Settings/Config Variable ACCESS_TOKEN to hold the secret Azumio API key.  
