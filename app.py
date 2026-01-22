from flask import Flask, request, make_response
from pytubefix import YouTube
from pytubefix.cli import on_progress

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index() -> any:
    #to use request
    if request.method == "GET":
        # to make custom responses
        response = make_response()
        response.status_code = 202
        response.headers['content-type'] = 'application/octet-stream'
        return "<h1>Hello World</h1>"
    elif request.method == "POST":
        return "<h1>You made a post request</h1>", 201  
    else:
        return "Request not valid"
    
@app.route('/add/<num1>/<num2>/')
def add(num1: any, num2: any) -> int:
    try:
        num1 = int(num1); num2 = int(num2)
    except Exception as e:
        print(f"Both inputs must be numbers but found {num1, num2}")
        return f"Both inputs must be numbers but found {num1, num2}"
    return f'{num1} + {num2} = {num1 + num2}'

@app.route('/download/')
def download_vide0() -> any:
    url = request.args.get('url')
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        video = yt.streams.get_highest_resolution()
        return video.download()
    except Exception as e:
        print(f'error: {e}')
        return f'Stopped the process in middle'

@app.route('/download-audio/')
def download_audioonly(url: any) -> any:
    url = request.args.get('url')
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        ys = yt.streams.get_audio_only()
        return  ys.download()
    except Exception as e:
        print(f'error: {e}')
        return f'Stopped the process in middle'



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5555, debug=True)