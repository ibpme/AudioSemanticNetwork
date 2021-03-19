from __future__ import unicode_literals
import youtube_dl
from os import path
import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import make_chunks
from vtt2text import convert_vtt

# TODO: Set saving directory to a Sample Directory


class SpeechToText(sr.Recognizer):

    def __init__(self, audio_filepath):
        # AUDIO_FILE = path.join(path.dirname(path.realpath(__file__)), "sample1.wav")
        self.recognizer = super().__init__()
        self.text = None
        self.audio = None
        self.filename = path.splitext(path.split(audio_filepath)[-1])[0]
        self.audio_filepath = audio_filepath

    # Large files could lead to error considerusing pyAudio for audio segmentation
    def get_text(self, write_to_file=False, language="id-ID"):
        with sr.AudioFile(self.audio_filepath) as source:
            self.audio = self.recognizer.record(source)
            self.text = self.recognizer.recognize_google(
                audio_data=self.audio, language=language)
        if write_to_file:
            self.write_to_file()
        return self.text

    def write_to_file(self):
        with open("{}.txt".format(self.filename), "w") as file:
            file.write(self.text)

    #!Unstable
    def get_text_chunk(self, chunk_length_ms=5000):
        myaudio = AudioSegment.from_file("{}.wav".format(self.filename), "wav")
        chunks = make_chunks(myaudio, chunk_length_ms)
        text = ""
        for audio_chunk in chunks:
            audio_chunk.export("temp", format="wav")
            with sr.AudioFile("temp") as source:
                audio = self.recognizer.listen(source)
                try:
                    # ?There might be a spacing problem
                    text += self.recognizer.recognize_google(audio)
                except Exception as ex:
                    print("Error occured")
                    print(ex)
        self.text = text
        if write_to_file:
            self.write_to_file()
        return text


class GetAudioFromYoutube():

    def __init__(self, url, title=False, codec='wav', download=True):
        self.ydl_opts = {
            'format': 'bestaudio/audio',
            'logger': self,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': codec,
            }],
            'progress_hooks': [self.my_hook],
        }
        self.url = url
        self.codec = codec
        self.info_dict = None
        self.video_id = None
        self.title = None

        if title:
            self.ydl_opts['outtmpl'] = title + ".%(ext)s"
            self.title = title
        if download:
            self.download_audio()

    def download_audio(self):
        with youtube_dl.YoutubeDL(self.ydl_opts) as ydl:
            self.info_dict = ydl.extract_info(self.url, download=True)
            self.video_id = self.info_dict.get("id", None)
            video_title = self.info_dict.get('title', None)
            if not self.title:
                self.title = video_title

    def list_subtitles(self):
        ydl_opts = {'listsubtitles': True}
        if self.title:
            ydl_opts['outtmpl'] = self.title + ".%(ext)s"
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.url])

    # TODO Check if subtitle is avaiable first then download auto-sub
    def write_subtitle(self, lang='id'):
        ydl_opts = {
            'writeautomaticsub': True,
            "skip_download": True, "subtitleslangs": [lang]}
        if self.title:
            ydl_opts['outtmpl'] = self.title + ".%(ext)s"
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([self.url])

    def debug(self, msg):
        print(msg)

    def warning(self, msg):
        print(msg)

    def error(self, msg):
        print(msg)

    def my_hook(self, hook):
        if hook['status'] == 'finished':
            print('Done downloading, now converting ...')


if __name__ == "__main__":
    print(convert_vtt("Najwa.id.vtt"))
