from ibm_watson import AssistantV2
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from watson_speech_to_text import record_audio
#from weather import get_weather_data
import requests
import random
import pygame
import pyaudio
import json
import speech_recognition as sr
import pyttsx3
import sys
import pydub
import time
import threading
import simpleaudio as sa
import random
import os
import difflib
from ibm_watson import TextToSpeechV1
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import json
from ibm_watson import SpeechToTextV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import wave
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
import webbrowser
import os
import base64
from requests import post

from pydub import AudioSegment
from pydub.playback import play

# Spotify API credentials
client_id = 'a5c2a4ce9c0c463fa474bf55fb0750c7'
client_secret = '34446cd588974b158fd968ce46bd608b'
redirect_uri = 'http://localhost:8888/callback'
username = 'ab4o1l8is3u3ssvxwbqobt4qo'

# Set up the Speech to Text service
apikey_speech_to_text = 'vIC0cr98ZS3tO7FxgceuzsjCrhDUjiMc2IbSEtSdEzjv'
url_speech_to_text = 'https://api.au-syd.speech-to-text.watson.cloud.ibm.com/instances/cbab904d-34fb-41dc-a0fd-40cca19ff9e6'
authenticator = IAMAuthenticator(apikey_speech_to_text)
speech_to_text = SpeechToTextV1(authenticator=authenticator)
speech_to_text.set_service_url(url_speech_to_text)

# Set up the Text to Speech service
apikey_text_to_speech = 'Hr1EeXcU03t3n9kXgNLGI6_7OaDpApVkVjfWaUuM3svT'
url_text_to_speech = 'https://api.eu-gb.text-to-speech.watson.cloud.ibm.com/instances/033cb2d2-2c96-450b-ac92-3eee1477221c'
authenticator = IAMAuthenticator(apikey_text_to_speech)
text_to_speech = TextToSpeechV1(authenticator=authenticator)
text_to_speech.set_service_url(url_text_to_speech)

def record_audio():
    sample_rate = 44100
    chans = 1
    chunk = 1024
    filename = 'audio.wav'
    duration = 5
    dev_index = 0
    # Initialize PyAudio
    audio_interface = pyaudio.PyAudio()
    print("Device count:")
    print(audio_interface.get_device_count())
    print("max input channels:")
    print(audio_interface.get_default_input_device_info()['maxInputChannels'])
    # Open the microphone stream
    try:
        stream = audio_interface.open(format = pyaudio.paInt16, rate=sample_rate, channels = chans, input_device_index = 0,input = True,frames_per_buffer=chunk)
    except:
        stream = audio_interface.open(format = pyaudio.paInt16, rate=sample_rate, channels = chans, input_device_index = 1,input = True,frames_per_buffer=chunk)
    # Start recording
    print("Recording started...")
    frames = []
    for i in range(0, int(sample_rate / chunk * duration)):
        data = stream.read(chunk, exception_on_overflow=False)
        frames.append(data)

    # Stop recording
    print("Recording ended!")
    stream.stop_stream()
    stream.close()
    audio_interface.terminate()

        # Open a wave file for writing
    wf = wave.open(filename, 'wb')

    # Set the audio file parameters
    wf.setnchannels(1)
    wf.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
    wf.setframerate(sample_rate)

    # Write the audio frames to the file
    wf.close()

def play_response(response_text):
    response_speech = text_to_speech.synthesize(response_text, accept='audio/wav', voice='en-US_AllisonV3Voice').get_result()
    print("playing response")
    # Save the audio to a file
    output_file = "output.wav"
    with open(output_file, 'wb') as audio_file:
        audio_file.write(response_speech.content)
    time.sleep(0.5)
    
    audio = AudioSegment.from_wav("output.wav")
    play(audio)
   
    



def get_weather_data():
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
    API_KEY = '417af52d6a054b1434bb65cbfd0f2ae2'
    CITY = 'London'

    url = BASE_URL + "appid=" + API_KEY + "&q=" + CITY
    response = requests.get(url).json()

    if response["cod"] == 200:
        kelvin_temperature = response["main"]["temp"]
        celsius_temperature = kelvin_temperature - 273.15  # Convert from Kelvin to Celsius

        weather_data = {
            "City": response["name"],
            "Weather": response["weather"][0]["description"],
            "Temperature": celsius_temperature,
            "Humidity": response["main"]["humidity"],
            "Wind Speed": response["wind"]["speed"],
            "Visibility": response["visibility"],
        }

        print("Weather in", weather_data["City"])
        print("Description:", weather_data["Weather"])
        #print("Temperature:", weather_data["Temperature"], "°C")
        #print("Humidity:", weather_data["Humidity"], "%")
        #print("Wind Speed:", weather_data["Wind Speed"], "m/s")
        #print("Visibility:", weather_data["Visibility"])

        # Determine the number based on the weather description
        description = weather_data["Weather"].lower()
        if description == "clear sky":
            print("sunny")
            play_response("it is sunny out there")

        elif description in ["few clouds", "scattered clouds", "broken clouds", "overcast clouds"]:
            print("cloudy")
            play_response("it is cloudy out there")

        elif description in ["mist", "fog", "haze", "smoke"]:
            print("foggy")
            play_response("it is foggy out there")

        elif description in ["light rain", "moderate rain", "heavy rain", "showers"]:
            print("rainy")
            play_response("it is rainy out there")

        elif description == "thunderstorm":
            print("thunderstorm")
            play_response("it is storming out there")

        elif description in ["snow", "light snow", "moderate snow", "heavy snow"]:
            print("snowy")
            play_response("it is snowy out there")

        else:
            print("Number: Unknown")

    else:
        print("Error:", response["message"])

def get_display_weather_data():
    print("getting display weather data")
    BASE_URL = "http://api.openweathermap.org/data/2.5/weather?"
    API_KEY = '417af52d6a054b1434bb65cbfd0f2ae2'
    CITY = 'London'

    url = BASE_URL + "appid=" + API_KEY + "&q=" + CITY
    response = requests.get(url).json()

    if response["cod"] == 200:
        kelvin_temperature = response["main"]["temp"]
        celsius_temperature = kelvin_temperature - 273.15  # Convert from Kelvin to Celsius

        weather_data = {
            "City": response["name"],
            "Weather": response["weather"][0]["description"],
            "Temperature": celsius_temperature,
            "Humidity": response["main"]["humidity"],
            "Wind Speed": response["wind"]["speed"],
            "Visibility": response["visibility"],
        }

        print("Weather in", weather_data["City"])
        print("Description:", weather_data["Weather"])
        #print("Temperature:", weather_data["Temperature"], "°C")
        #print("Humidity:", weather_data["Humidity"], "%")
        #print("Wind Speed:", weather_data["Wind Speed"], "m/s")
        #print("Visibility:", weather_data["Visibility"])

        # Determine the number based on the weather description
        description = weather_data["Weather"].lower()
        #cloud, drizzle, night, nightcloud, rain, snow, sun, suncloud, thunder
        if description == "clear sky":
           return "sun"
        
        elif description in ["few clouds", "scattered clouds", "broken clouds"]:
            return "suncloud"

        elif description == "overcast clouds":
            return "cloud"
        
        elif description in ["mist", "fog", "haze", "smoke"]:
            return "thunder"

        elif description in ["light rain", "showers"]:
            return "drizzle"
        
        elif description in ["moderate rain", "heavy rain"]:
            return "rain"

        elif description == "thunderstorm":
            return "thunder"
            
        elif description in ["snow", "light snow", "moderate snow", "heavy snow"]:
            return "snow"
        
        else:
            return "suncloud"




def spotify_podcast_find(podcast_name, episode_name):
    # Create OAuth Object
    oauth_object = spotipy.SpotifyOAuth(client_id,client_secret,redirect_uri)

    # Create token
    token_dict = oauth_object.get_access_token()
    token = token_dict['access_token']

    # Create Spotify Object
    spotifyObject = spotipy.Spotify(auth=token)

    # Create a Spotipy client with user authorization
    scope = 'user-read-playback-state,user-modify-playback-state'
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))

    # Search for a podcast
    #podcast_name = 'The News Agent'
    #episode_name = 'Lord, Ladies, and Boris Johnson honour'
    results = sp.search(q=f'podcast:{podcast_name} episode:{episode_name}', type='episode', limit=1)

    # Extract the URI of the first track found
    if len(results['episodes']['items']) > 0:
        episode_uri = results['episodes']['items'][0]['uri']
        print("Episode URI:", episode_uri)

        # Play the song
        devices = sp.devices()
        if len(devices['devices']) > 0:
            device_id = devices['devices'][0]['id']
            sp.start_playback(device_id=device_id, uris=[episode_uri])
            print("Playing the podcast...")
            #print(device_id)
        else:
            print("No active devices found.")
    else:
        print("Podcast not found.")


def spotify_track_find_and_play():
    client_id = 'a5c2a4ce9c0c463fa474bf55fb0750c7'
    client_secret = '34446cd588974b158fd968ce46bd608b'
    # Create OAuth Object
    oauth_object = spotipy.SpotifyOAuth(client_id,client_secret,redirect_uri, cache_path='/__pycache__/.cache')
    print("got this far")
    # Create token
    def get_token():
        auth_string = client_id + ":" + client_secret
        auth_bytes = auth_string.encode("utf-8")
        auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

        url = "https://accounts.spotify.com/api/token"
        headers = {
            "Authorization": "Basic " + auth_base64,
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {"grant_type": "client_credentials"}
        result = post(url, headers=headers, data=data)
        json_result = json.loads(result.content)
        token = json_result["access_token"]
        return token

    token = get_token()
    print(token)

    # Create Spotify Object
    spotifyObject = spotipy.Spotify(auth=token)

    # Create a Spotipy client with user authorization
    scope = 'user-read-playback-state,user-modify-playback-state'
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))
    print("starting to record audio")
    record_audio()
    print("finished recording audio")
    recognizer = sr.Recognizer()
    print("google recognise")
    try:
        with sr.AudioFile('audio.wav') as source:
            audio = recognizer.record(source)
            # self.lastAudioInput = recognizer.recognize_google(audio)
            recognized_text = recognizer.recognize_google(audio)
            print("audio input was: ", recognized_text)
    except:
        print("ahh didnt work")
    try:
        with open('audio.wav', 'rb') as audio:
            response = speech_to_text.recognize(audio=audio, content_type='audio/wav')
            track_information = response.result['results'][0]['alternatives'][0]['transcript']
            #return text
            track_name = track_information
            update_tracklist(track_name)
            results = sp.search(q=track_name, type='track', limit=1)

    except :
        print("Speech recognition could not understand audio.")
        print("not playing music")
        return 
    # Extract the URI of the first track found
    if len(results['tracks']['items']) > 0:
        song_uri = results['tracks']['items'][0]['uri']
        print("Song URI:", song_uri)

        # Play the song
        devices = sp.devices()
        if len(devices['devices']) > 0:
            device_id = devices['devices'][0]['id']
            sp.start_playback(device_id=device_id, uris=[song_uri])
            print("Playing the song...")
            print(device_id)
        else:
            print("No active devices found.")
    else:
        print("Song not found.")

def spotify_track_find_and_play_v2(track_name):
    # Create OAuth Object
    oauth_object = spotipy.SpotifyOAuth(client_id,client_secret,redirect_uri)

    # Create token
    token_dict = oauth_object.get_cached_token()
    token = token_dict['access_token']

    # Create Spotify Object
    spotifyObject = spotipy.Spotify(auth=token)

    # Create a Spotipy client with user authorization
    scope = 'user-read-playback-state,user-modify-playback-state'
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))
    
    try:
        with open('audio.wav', 'rb') as audio:
            response = speech_to_text.recognize(audio=audio, content_type='audio/wav')
            track_information = response.result['results'][0]['alternatives'][0]['transcript']
            return text
            
            update_tracklist(track_name)
            results = sp.search(q=track_name, type='track', limit=1)


    except :
        print("Speech recognition could not understand audio.")

    # Extract the URI of the first track found
    if len(results['tracks']['items']) > 0:
        song_uri = results['tracks']['items'][0]['uri']
        print("Song URI:", song_uri)

        # Play the song
        devices = sp.devices()
        if len(devices['devices']) > 0:
            device_id = devices['devices'][0]['id']
            sp.start_playback(device_id=device_id, uris=[song_uri])
            print("Playing the song...")
            print(device_id)
        else:
            print("No active devices found.")
    else:
        print("Song not found.")




def spotify_podcast_find_and_play():
    # Create OAuth Object
    oauth_object = spotipy.SpotifyOAuth(client_id,client_secret,redirect_uri)

    # Create token
    token_dict = oauth_object.get_cached_token()
    token = token_dict['access_token']

    # Create Spotify Object
    spotifyObject = spotipy.Spotify(auth=token)

    # Create a Spotipy client with user authorization
    scope = 'user-read-playback-state,user-modify-playback-state'
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri, scope=scope))

    record_audio()
    try:
        with open('audio.wav', 'rb') as audio:
            response = speech_to_text.recognize(audio=audio, content_type='audio/wav')
            podcast_information = response.result['results'][0]['alternatives'][0]['transcript']
            #return text
            podcast_name = podcast_information
            episode_name = "episode 1"
            results = sp.search(q=f'podcast:{podcast_name} episode:{episode_name}', type='episode', limit=1)


    except :
        print("Speech recognition could not understand audio.")

    # Extract the URI of the first track found
    if len(results['episodes']['items']) > 0:
        podcast_uri = results['episodes']['items'][0]['uri']
        print("Podcast URI:", podcast_uri)

        # Play the song
        devices = sp.devices()
        if len(devices['devices']) > 0:
            device_id = devices['devices'][0]['id']
            sp.start_playback(device_id=device_id, uris=[podcast_uri])
            print("Playing the podcast...")
            print(device_id)
        else:
            print("No active devices found.")
    else:
        print("Podcast not found.")

def update_tracklist(new_text):
    file_name = "tracklist.txt"  # Name of the text file to update

    try:
        with open(file_name, "r+") as file:
            current_text = file.read()
            updated_text = current_text + "\n" + new_text
            file.seek(0)  # Move the file pointer to the beginning of the file
            file.write(updated_text)
        print("Tracklist updated successfully!")
    except FileNotFoundError:
        print("The tracklist file does not exist.")
    except IOError:
        print("An error occurred while updating the tracklist.")

# Example usage
#input_text = input("Enter the text to update the tracklist: ")
#update_tracklist(input_text)

#def extract_random_line(file_name):
#    try:
#        with open(file_name, "r") as file:
#            lines = file.readlines()
#            random_line = random.choice(lines).strip()
#            return random_line
#    except FileNotFoundError:
#        print("The file does not exist.")
#        return None
#    except IOError:
#        print("An error occurred while reading the file.")
#        return None

# Example usage
#file_name = "tracklist.txt"  # Name of the text file to read
#random_line = extract_random_line(file_name)
#if random_line:
#    print("Random line:", random_line)

def play_podcast(file_path):

    wave_obj = sa.WaveObject.from_wave_file(file_path)
    play_obj = wave_obj.play()

    stop_playing = False

    while not stop_playing:

        record_audio()
        try:
            with open('audio.wav', 'rb') as audio:
                response = speech_to_text.recognize(audio=audio, content_type='audio/wav')
                text = response.result['results'][0]['alternatives'][0]['transcript']
                print(text)
                if("stop" in text or "pause" in text or "terminate" in text or "yes" in text):
                    stop_playing = True
                    play_obj.stop()
                    #play_response("The audio is now paused")
                    print("The audio is now paused")
                
                else:
                    #play_response("I cannot assist you properly while playing an audio. Can I pause the audio first?")
                    print("I cannot assist you properly while playing an audio. Can I pause the audio first?")

        except :
            print("No sound detected")
            pass

def search_and_play_song(song_name):
    search_directory = r"/home/pi/songs"  # Update this with the desired directory path

    # Search for WAV files in the specified directory
    wav_files = []
    for root, dirs, files in os.walk(search_directory):
        for file in files:
            if file.endswith(".wav"):
                wav_files.append(file)

    # Find the closest matching song
    closest_match = difflib.get_close_matches(song_name, wav_files, n=1, cutoff=0.5)

    if closest_match:
        # Get the selected song file
        song_file = os.path.join(search_directory, closest_match[0])
        #print(song_file)

        # Play the selected song
        wave_obj = sa.WaveObject.from_wave_file(song_file)
        play_obj = wave_obj.play()

        stop_playing = False

        while not stop_playing:

            record_audio()
            try:
                with open('audio.wav', 'rb') as audio:
                    response = speech_to_text.recognize(audio=audio, content_type='audio/wav')
                    text = response.result['results'][0]['alternatives'][0]['transcript']
                    print(text)
                    if("stop" in text or "pause" in text or "terminate" in text or "yes" in text):
                        stop_playing = True
                        play_obj.stop()
                        #play_response("The audio is now paused")
                        print("The audio is now paused")
                    
                    else:
                        #play_response("I cannot assist you properly while playing an audio. Can I pause the audio first?")
                        print("I cannot assist you properly while playing an audio. Can I pause the audio first?")

            except :
                print("No sound detected")
                pass

        # Wait for the song to finish playing
        #play_obj.wait_done()
    else:
        print("Song not found!")


def play_random_song(directory):
    # Search for WAV files in the specified directory
    wav_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".wav"):
                wav_files.append(os.path.join(root, file))

    if wav_files:
        # Select a random WAV file
        random_song = random.choice(wav_files)
        print(random_song)

        # Play the selected song
        wave_obj = sa.WaveObject.from_wave_file(random_song)
        play_obj = wave_obj.play()

        stop_playing = False

        while not stop_playing:

            record_audio()
            try:
                with open('audio.wav', 'rb') as audio:
                    response = speech_to_text.recognize(audio=audio, content_type='audio/wav')
                    text = response.result['results'][0]['alternatives'][0]['transcript']
                    print(text)
                    if("stop" in text or "pause" in text or "terminate" in text or "yes" in text):
                        stop_playing = True
                        play_obj.stop()
                        #play_response("The audio is now paused")
                        print("The audio is now paused")
                    
                    else:
                        #play_response("I cannot assist you properly while playing an audio. Can I pause the audio first?")
                        print("I cannot assist you properly while playing an audio. Can I pause the audio first?")

            except :
                print("No sound detected")
                pass
    else:
        print("No WAV files found in the directory!")