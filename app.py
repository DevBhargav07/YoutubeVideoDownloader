from flask import Flask, request, make_response, render_template, send_file
from pytubefix import YouTube
from pytubefix.cli import on_progress
import os

app = Flask(__name__, template_folder='templates')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "VIDEO_DIR")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

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

@app.route('/download-video/', methods=["POST"])
def download_vide0() -> any:
    url = request.args.get('url')
    print(f'url is :{url}')
    if not url: url = request.form.get('yturl')
    print(url)
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        video = yt.streams.get_highest_resolution()
        # file_path = os.path.join(DOWNLOAD_DIR, f"{video.download()}")
        # print(f'file path is {os.path.abspath(file_path)}')
        file_path = video.download(output_path=DOWNLOAD_DIR)
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"{yt.title}",
            mimetype="video/mp4"
        )
    except Exception as e:
        # yt = YouTube(url, use_oauth=True, allow_oauth_cache=True, on_progress_callback=on_progress)
        # video = yt.streams.get_highest_resolution()
        # return video.download()
        
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
        # yt = YouTube(url, use_oauth=True, allow_oauth_cache=True, on_progress_callback=on_progress)
        # ys = yt.streams.get_audio_only()
        # return  ys.download()
        print(f'error: {e}')
        return f'Stopped the process in middle'

@app.route('/download/')
def download_page() -> any:
    return render_template('index.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5555, debug=True)