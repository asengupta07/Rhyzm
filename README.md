# RHYZM
<!-- ## Video Demo:  <URL HERE> -->
## Description:
Rhyzm is a responsive music downloader web application that is built using python on top of Flask and Jinja framework. The music data is provided by Spotify API and the song is downloaded using Pytube python library with the help of Youtube Data API.

## Usage:
First, you should install all required libraries for this application to run bt executing the following command in the terminal:

    pip install -r requirements.txt

To start the web application server, in the project directory, execute the following in the terminal:
    
    flask run
This will start a development server. Click the link shown in the terminal to access the login page of the application. 

If you are a new user, you will need to register first. To do so, simply click on the Register option in the navbar menu. 

After registration, log in with your credentials to access the index page which shows the Top 50 Global Hits from the Spotify Playlist of the same name. 

Using the navbar, you may click on the Search option to search for songs to download, the Download History option to view your past downloads, or the Logout option to do just that.

When you click on the Search option you are redirected to the Search page where you can enter a Search Query and the Number of Results you want to view, and after clicking on the Search button you will find a list of the Search results. You may download one or more of the songs from the results using the Download button beside each listed result.

When you click on the Download History, you can which songs you have downloaded, how many times you have downloaded each of them and the total number of songs you have downloaded.

Finally the Log Out option logs you out of the system, and the next time you want to use the application, you must log in.

When you want to stop the server, simply press Ctrl+C in the terminal to do so.

## Files and Folders:
### ***1. project.py***
This is the main project file that does most of the heavy lifting in the application including authenticating API keys, getting Access Tokens, reading API responses, formatting API responses and downloading required files to the server when need be.

Originally project.py was supposed to be the only file in the project, making it so that the application would have been command-line based. However, in favour of accessibility, user experience and to make the project a little bit more challenging, I decided to make this a web application with app.py. However, I have retained the command line usage of the project too which can be used by executing the following command:
    
    python3 project.py


### ***2. app.py:***
app.py contains the Flask framework including routes, session configurations and database management. On running the command
    
    flask run
the app.py file is automatically run as the server using Flask framework as per the [Flask Documentation - Application Discovery Behavior](https://flask.palletsprojects.com/en/2.3.x/quickstart/).

### ***3. test_project.py***
test_project.py contains unit tests for some project.py functions using the pytest library

### ***4. templates:***
The templates folder contains the html templates that are rendered using Flask in app.py

### ***5. static:***
The static folder contains all the static properties that may be requested by the browser to load one or more templates. This includes font files, css file, favicon and other images used in the website.

### ***6. rhyzm.db:***
It is the database that contains user information including hashed credentials, download history and all other relevant data.

#### ***7. requirements.txt:***
It contains information about the pip installable packages that must be installed before running the application.

### ***8. .env:***
This is a very important file that you must create on your own that contains YouTube Data API keys and Spotify Client ID as well as Client Secret. Since YouTube Data API allows [10,000 units/day](https://developers.google.com/youtube/v3/guides/quota_and_compliance_audits) and every single query costs [100 units](https://developers.google.com/youtube/v3/determine_quota_cost), only 100 downloads per day is possible for each key. So as a workaround, we can include more than one key as a JSON list. Hence the variables should be included in the .env file in the following format:

    API_KEY = '["<api-key>", ...]'
    CLIENT_ID = "<client id>"
    CLIENT_SECRET = "<client secret>"
***P.S: API_KEY should always be a list, even if it is a single key.***

## Note:
I do not own or claim to own any data, information, media and/or intellectual property that is presented, distributed and/or used in this project. All of this aforementioned data is used in this project non-commercially and strictly for research/educational purposes.