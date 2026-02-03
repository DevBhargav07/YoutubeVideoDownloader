from flask import Flask, request, render_template, send_file, jsonify, after_this_request, redirect, url_for
from pytubefix import YouTube
from pytubefix.cli import on_progress
import os, io, logging

logging.basicConfig(
    filename='application.log',
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

app = Flask(__name__, template_folder='templates')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VIDEO_DIR = os.path.join(BASE_DIR, "VIDEO_DIR")
AUDIO_DIR = os.path.join(BASE_DIR, 'AUDIO_DIR')
CAPTIONS_DIR = os.path.join(BASE_DIR, "CAPTIONS_DIR")
os.makedirs(VIDEO_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(CAPTIONS_DIR, exist_ok=True)

@app.route('/add/<num1>/<num2>/')
def add(num1: any, num2: any) -> int:
    try:
        num1 = int(num1)
        num2 = int(num2)
    except Exception as e:
        print(f"Both inputs must be numbers but found {num1, num2}")
        return f"Both inputs must be numbers but found {num1, num2}"
    return f'{num1} + {num2} = {num1 + num2}'


@app.route('/download-video/', methods=["POST"])
def download_video() -> any:
    url = request.args.get('url')
    if not url: 
        url = request.form.get('yturl')
    
    if not url:
        return jsonify({'message': 'URL is required'}), 400
    
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        video = yt.streams.get_highest_resolution()
        if not video:
            return jsonify({'success': False, 'message': 'No video stream available for this URL'}), 404        
        file_path = video.download(output_path=VIDEO_DIR)

        with open(file_path, mode='rb') as f:
            data = io.BytesIO(f.read())
        @after_this_request
        def remove_file(response):
            try:
                os.remove(file_path)
            except Exception as error:
                app.logger.error(f'Got an error {error}')
            return response
        return send_file(
            data,
            as_attachment=True,
            download_name=f'{yt.title}.mp4',
            mimetype="video/mp4"
        )
    except Exception as e:
        error_message = str(e)
        app.logger.error(f'Error in download_video: {error_message}')

        if "unavailable" in error_message.lower():
            return jsonify({'success': False, 'message': 'Video is unavailable or private'}), 404
        elif "regex" in error_message.lower() or "video id" in error_message.lower():
            return jsonify({'success': False, 'message': 'Invalid YouTube URL. Please check and try again.'}), 400
        else:
            return jsonify({'success': False, 'message': f'Failed to download video: {error_message}'}), 400

@app.route('/download-audio/', methods=['POST'])
def download_audio() -> any:
    url = request.args.get('url')
    if not url: 
        url = request.form.get('ytaurl')
    
    if not url:
        return jsonify({'success': False, 'message': 'URL is required'}), 400
    
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        audio = yt.streams.get_audio_only()
        if not audio:
            return jsonify({'success': False, 'message': 'No audio stream available for this URL'}), 404
        file_path = audio.download(output_path=AUDIO_DIR)
        with open(file_path, mode='rb') as f:
            data = io.BytesIO(f.read())
        
        @after_this_request
        def remove_file(response) -> any:
            try:
                os.remove(file_path)
            except Exception as error:
                app.logger.error(f'Got an error {error}')
            return response
        
        return send_file(
            data,
            as_attachment=True,
            download_name=f'{yt.title}.webm',
            mimetype="audio/webm"
        )
    except Exception as e:
        error_message = str(e)
        app.logger.error(f'Error in download_audio: {error_message}')

        if "unavailable" in error_message.lower():
            return jsonify({'success': False, 'message': 'Video is unavailable or private'}), 404
        elif "regex" in error_message.lower() or "video id" in error_message.lower():
            return jsonify({'success': False, 'message': 'Invalid YouTube URL. Please check and try again.'}), 400
        else:
            return jsonify({'success': False, 'message': f'Failed to download audio: {error_message}'}), 400

@app.route('/captions/', methods=["POST", 'GET'])
def check_captions() -> any:
    """
    Docstring for check_captions
    Takes an url and check for captions if available
    -> Please note auto generated captions will not noted as captions. (can't be downloaded here.)
    :return: returns how many captions are available
    :rtype: String
    """
    url = request.args.get("url")
    if not url: 
        return jsonify({'message': 'URL is required'}), 400
    
    check = request.args.get("check")
    languages = {
        'a.en': "English", 
        "a.es": "Spanish", 
        "a.pt": "Portuguese", 
        "a.ru": "Russian", 
        "a.ar": "Arabic", 
        "a.fr": "French", 
        "a.de": "German", 
        "a.ja": "Japanese", 
        "a.zh-Hans": "Chinese"
    }
    
    try:
        yt = YouTube(url)
        
        if check:
            return jsonify({
                'captions': str(yt.captions),
                'caption_list': list(yt.captions)
            })
        
        download_captions = request.args.get("download")
        if download_captions:
            language = request.args.get("lang")
            captions = yt.captions
            return jsonify({'message': 'Caption download not implemented yet'}), 501
        
        return jsonify({'message': 'Please specify check=true or download=true'}), 400
        
    except Exception as e:
        print(f'Got an error: {e}')
        return jsonify({'message': f'Error: {str(e)}'}), 500

@app.route('/')
def download_page() -> any:
    return render_template('index.html')

#now we will know how to use template filters
@app.route('/learning/')
def learning_page() -> str:
    Name = "learner"
    return render_template("learning.html", Name=Name)

@app.template_filter('reverse_string')
def reverse_string(s) -> str:
    return s[::-1]

@app.template_filter("repeat")
def repeat(s, times=0) -> str:
    return s * times

@app.template_filter("alternate")
def alternate_letter(s):
    return "".join([s[i].upper() if i % 2 == 0 else s[i].lower() for i in range(len(s))])

@app.route('/redirect/')
def redirect_page():
    return redirect(url_for('learning_page'))

@app.route('/login/', methods=["GET", "POST"])
def login():
    userDetails = {"User": "admin@123", "admin": "admin@123"}
    if request.method=="GET":
        return render_template("login.html")
    elif request.method=="POST":
        username = request.form.get("Username")
        password = request.form.get("Password")
        try:
           if userDetails[f'{username}'] == password:
               return "Login Sucess", 200
           else:
               return "Login Failed!", 400
        except Exception as e:
            return "User details Not Found", 404


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5555, debug=True)