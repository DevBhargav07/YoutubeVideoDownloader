#Downloading youtube video using flask + python

First Install Python in your system

After installing the Python, check the version using the command

python --version

If no error occurs then python installed successfully and

Create a virtual environment using the below command

python -m venv env (use your preferred name)

Upon creating the venv, activate

For macos, linux

source env/bin/activate

For windows

.\env\Scripts\Activate

after that clone our project

then change your directory to the project directory simply perform the below command

pip install -r requirements or pip install -r requirements.txt

The above command will try to install all the requirements of the project which are needed for this project

Then run the project using command 

python app.py

which will run the project at http://127.0.0.1:5555

So, The information of code and using is explained below.

Using the Package called as pytubefix
-> Using os module base_directory to link the project file path using code or dynamically
-> Using the In-built concept in pytubefix to download the file inside of the respected_directory
-> Using the Flash In-built code to download the file to the user device
Written for both Video and Audio

Video:-
-> A input box to take the url for downloading either a video or audio  

#Captions are a bit of tricky to handle that
i got in a loop that i have to add that to the file or just give another input to
take that yt_video and download it seperately.
will look and try to find a seperate way.

In my Learning Way of Flask, This is my project
As using flask with python is a good project which uses a youtube url to download 
either an audio or video with a meaningful notifications for the user understanding
purpose.