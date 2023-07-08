import time
import sys
import random
from datetime import datetime
import pytz
from timeit import default_timer
import pyaudio
import RPi.GPIO as GPIO
import wave
import pydub
import simpleaudio
import speech_recognition as sr
from ctypes import *
from contextlib import contextmanager
import requests
import uuid
import os
import json
from PIL import Image
import pyttsx3
import gtts
import threading
from ibm_watson import AssistantV2
from ibm_watson import SpeechToTextV1
from nlp import hasTime, hasDate, getOccurence, getStrongestEmotion, categoriseText
from newsapiFile import getTopNewsHeadlines
#from phone import receive_data
import pygame
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
from pydub import AudioSegment
from pydub.playback import play
from watson_assistant_functions import spotify_track_find_and_play
from watson_assistant_functions import get_weather_data
from watson_assistant_functions import get_display_weather_data
from watson_assistant_functions import play_response
from watson_assistant_functions import spotify_podcast_find
from watson_assistant_functions import record_audio
from watson_assistant_functions import spotify_track_find_and_play_v2
from watson_assistant_functions import play_podcast
from watson_assistant_functions import search_and_play_song
from watson_assistant_functions import play_random_song
from calendarFile import Event, Day, CalendarClass
from smsapiFile import sendSMS
from emailFile import list_emails, getService, getNewEmails
#from weather import Weather
GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
from flask import Flask, request

import board
import busio
# Import MPR121 module.
import adafruit_mpr121

# Set up the Watson Assistant credentials
api_key = 'p7Fj1Ty5O5Qi_BWHYehHC1jA3ai2r14wgyRlqghSJe8u'
assistant_url = 'https://api.eu-gb.assistant.watson.cloud.ibm.com/instances/90bab243-6d6c-4c20-915e-b9c50e07883a'
assistant_id = '89672e43-8b25-4ee6-bf98-81c10aab9800'
action_skill_id = 'aeb1f59d-0354-483e-8730-52c792c569e3'
dialog_skill_id = 'db4c637a-587d-489f-82fc-eabdd9122335'
draft_environment_id = 'e327fd2f-fb3b-4117-96f9-2746faa0fa3d'
live_environment_id = 'c10287b5-463e-4c01-82a2-7988df39a298'

# Set up the Speech to Text service
apikey_speech_to_text = 'vIC0cr98ZS3tO7FxgceuzsjCrhDUjiMc2IbSEtSdEzjv'
url_speech_to_text = 'https://api.au-syd.speech-to-text.watson.cloud.ibm.com/instances/cbab904d-34fb-41dc-a0fd-40cca19ff9e6'
authenticator = IAMAuthenticator(apikey_speech_to_text)
speech_to_text = SpeechToTextV1(authenticator=authenticator)
speech_to_text.set_service_url(url_speech_to_text)

# Set up the Text to Speech service
apikey_text_to_speech = 'mMMNbtTKGFh2v6oadSUIcx2nShoSQHoqz-j-3b221psW'
url_text_to_speech = 'https://api.eu-gb.text-to-speech.watson.cloud.ibm.com/instances/e8406218-8ee7-446d-b99a-435715492be3'
authenticator = IAMAuthenticator(apikey_text_to_speech)
text_to_speech = TextToSpeechV1(authenticator=authenticator)
text_to_speech.set_service_url(url_text_to_speech)

# Spotify API credentials
client_id = 'a5c2a4ce9c0c463fa474bf55fb0750c7'
client_secret = 'classified'
redirect_uri = 'http://localhost:8888/callback'
username = 'classified'

# Authenticate with Watson Assistant
authenticator = IAMAuthenticator(api_key)
assistant = AssistantV2(
    version='2021-11-27',
    authenticator=authenticator
)

assistant.set_service_url(assistant_url)

#response=assistant.get_workspace(workspace_id=dialog_skill_id).get_result()

# Create a session with Watson Assistant
session = assistant.create_session(draft_environment_id).get_result()
#session = assistant.create_session(live_environment_id).get_result()
session_id = session['session_id']





class Pet:
    def __init__(self):
        

        self.petState = 0
        #0 is idle (goes to either state 1 or 3)
        #1 is listening (goes to either state 0 or 2)
        #2 is replying (goes to either 0 or 1)
        #3 is seeking attention (goes to either 0 or 1)
        self.userName = ""
        self.location = "London"
        self.emailAddress = ""
        self.contactNumber = ""
        self.spUsername = ""
        self.spPassword = ""
        self.happinessLevel = 10.0
        #happiness level is minimum 0, maximum 10 (different emotion face for every 2 levels, so we need 5 emotion faces)
        #below happiness level of 5, the pet begins to seek attention
        #how often the pet seeks attention increases until happiness level 2, then begins to decrease (the pet is now low energy) (so rise and then fall between 0 and 5, like a bell curve )
        
        self.animalType = "cat" #we are assuming its dog for now, but we can eventually change this to also include cat
        self.unhappinessTimer = time.time()
        self.lastAudioInput = ""
        self.displayWeather = "suncloud"
        self.reply_text = "Hello, My name is NOVA. How can I help you today?" # Default reply text for replystate.

        self.seekattention_text = "Hi, Where are you?" # When the state becomes seekattention_state, NOVA speaks seekattention_text
        self.eventsToAnnounce = []
        self.counter = 0 #counts the number of waiting state of NOVA
        self.trackcounter = 0 # counts the number of tracks in the tracklist
        self.seekattention_counter = 0 #counts the number of visiting seekattentionState
        self.emergency_counter = 0
        # self.emailService = getService()
        self.prevTime = int(time.time())
        self.calendar = CalendarClass(currentDayIndex=0)#change this to be the correct day at some point
        button_t = threading.Thread(target=self.button_thread)
        button_t.start()
        self.alarmSound = ""
        notification_t = threading.Thread(target=self.notification_thread)
        notification_t.start()

        display_thread_t = threading.Thread(target=self.display_thread)
        display_thread_t.start()


        

        # ------------ HAPPINESS LEVEL CODE --------------------------------------------------------------
    def increase_happiness_level(self,increaseValue): 
        self.happinessLevel = min(10, self.happinessLevel + increaseValue)

    def decrease_happiness_level(self,decreaseValue):
        self.happinessLevel = max(0, self.happinessLevel - decreaseValue)
    # ------------------------------------------------------------------------------------------------

        #------------CODE FOR ANY THREADS WHICH RUN CONSTANTLY--------------------------------------------------------------------------

    def button_thread(self): #(this function calls increase happiness level)
        # this function will be run as a thread constantly (you should constantly be able to detect a button press)

        # Create I2C bus.
        i2c = busio.I2C(board.SCL, board.SDA)

        # Create MPR121 object.
        mpr121 = adafruit_mpr121.MPR121(i2c)
        # Loop forever testing each input and printing when they're touched.
        while True:

            if not GPIO.input(18):#replace with wherever the button is
                #button has been pressed
                self.increase_happiness_level(0.2)
                if(self.petState == 0 or self.petState == 3):
                    self.petState = 1
                elif self.petState == 4:
                    self.petState = 0
                print("button pressed")
                

            if self.petState == 0:
                
                for i in range(12):
                # Call is_touched and pass it then number of the input.  If it's touched
                # it will return True, otherwise it will return False.
                    if mpr121[i].value:
                        print("increasing happiness level because of stroking")
                        self.increase_happiness_level(0.05)
            time.sleep(1)
    
    
       
    def display_thread(self):
        displayOn = True
        animalNotWeather = 0
        
        display_width = 1920

        display_height = 1080
        white = (255, 255, 255)
        pygame.init()
        gameDisplay = pygame.display.set_mode((display_width, display_height))
        
        def ImgFunction(x, y):
            gameDisplay.blit(Img, (x, y))
        while True:
            time.sleep(1)
            if displayOn:
                if self.petState != 0:
                    displayOn = False
                    pygame.quit()
                    continue
                if animalNotWeather > 7:
                    animalFace = min(4, int(self.happinessLevel // 2))
                    image = self.animalType + str(animalFace) + ".bmp"
                    #display animal image
                else:
                    if self.displayWeather == "suncloud":
                        image = "cloudsun.bmp"
                    else:
                        image = self.displayWeather + ".bmp"
                    #display weather image
                Img = pygame.image.load(image)
                Img = pygame.transform.scale(Img, (display_width, display_height))
                animalNotWeather+=1
                if animalNotWeather > 10:
                    animalNotWeather = 0
                
                
                
                x = (display_width - Img.get_width()) /2
                y = (display_height - Img.get_height())/2
            

                gameDisplay.fill(white)
                ImgFunction(x, y)

                pygame.display.update()
                
            
            else:
                if self.petState == 0:
                    time.sleep(2)
                    print("11")
                    displayOn = True
                    pygame.init()
                    print("22")
                    gameDisplay = pygame.display.set_mode((display_width, display_height))
                    print("33")
            

    def notification_thread(self):
        current_time = time.time()
        counter = 0
        while True:
            time.sleep(10)
            counter+=1
            counter = min(10, counter)
            if self.petState==0:
                print("checking for notifications")
                current_time = time.time()

                tz_London = pytz.timezone('Europe/London')

                # Get the current time in London
                datetime_London = datetime.now(tz_London)

                # Format the time as a string and print it
                dayTime = datetime_London.strftime("%H%M")


                # get day of week as an integer
                dayIndex = datetime_London.weekday()
                
                newAnnouncement = self.calendar.checkAnnouncements(dayTime)#change it to be the current time
                if newAnnouncement == "alarm":
                    self.alarmSound = "alarm"
                    self.petState = 4
                elif newAnnouncement:
                    self.alarmSound = newAnnouncement
                    self.petState = 4

                self.calendar.possibleChangeDay(dayIndex)
                # getNewEmails(self.emailService, self.prevTime) #this prints
                self.prevTime = int(time.time())
                if counter >= 10:
                    counter = 0
                    self.displayWeather = get_display_weather_data()
                    print("weather on display is now: ", self.displayWeather)

  

#


    #----------------------------------------------------------------------------------------------------------------------------------

    #CODE FOR STATES

    def initiateProb(self, happinessLevel, animalType):#check if values are okay
        if animalType == "dog":
            multiplier = 1.25
        else:
            multiplier = 1
        if happinessLevel < 1.0:
            return 0.8*multiplier
        elif happinessLevel < 2.0:
            return 0.5*multiplier
        elif happinessLevel < 3.0:
            return 0.3*multiplier
        elif happinessLevel < 4.0:
            return 0.2*multiplier
        elif happinessLevel < 5.0:
            return 0.1*multiplier
        else:
            return 0
        
    def idleState(self): #(this calls decrease happiness level)(ALEERA)
        #in this function you:
            # 1. display the current emotion level
            # 2. display the whether
            # (^^ these display tasks will be called by calling functions defined in screen.py)
            # 3. check for notifications (don't do this yet)
            # 4. update happiness level (based on time since last interaction) y
            # 5. based on happiness level maybe switch to the seek attention state y
        time.sleep(1)
        print(self.userName)
        if(time.time()-self.unhappinessTimer > 15):#this is the number to set how often it gets less happy
            print("becoming less happy")
            self.decrease_happiness_level(0.2)
            self.unhappinessTimer = time.time()
            randomNum = random.random()
            print("randomNum: ", randomNum)
            print(self.userName)
            print(self.contactNumber)
            # if randomNum < (self.initiateProb(self.happinessLevel, self.animalType)):
            if randomNum < 1:
                self.petState = 3
            #if self.happinessLevel < 1.0:
             #   if randomNum < 0.2:
              #      self.petState = 3
            #elif self.happinessLevel < 2.0:
             #   if randomNum < 0.4:
              #      self.petState = 3
            #elif self.happinessLevel < 3.0:
             #   if randomNum < 0.8:
              #      self.petState = 3
            #elif self.happinessLevel < 4.0:
             #   if randomNum < 0.5:
              #      self.petState = 3
            #elif self.happinessLevel < 5.0:
             #   if randomNum < 0.3:
              #      self.petState = 3
        print("in idle state. happinss level: ", self.happinessLevel)
        #display stuff -> get the emotion level and display the face
        #get the weather -> display the weather
        

        #announcing calendar events
        while len(self.eventsToAnnounce) > 0:
            event = self.eventsToAnnounce.pop(0)
            print("you have ", event, " coming up in less than 15 minutes")#needs to be replaced with the speaker


    def listenState(self): #kihyun
        #in this function you:
        #listen for 10 seconds using mic
        #save this audio to a file
        #translate the audio file into text
        #save text in self.lastAudioInput
        #save this audio to a file called 'audio.wav'
        #print("CHECKPOINT ALEERA")
        #if(self.userName == ""):
            #print("Please submit your details through the app") #through speaker
         #   play_response("Please submit your details through the app.")
          #  self.petState = 0
        #else:


            print("in listen state")
            # Set the sample rate, channels, and chunk size

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
            wf.writeframes(b''.join(frames))
            wf.close()
            self.unhappinessTimer = time.time()
            self.decideTask() #go straight to processing
      

        
    def decideTask(self): #kihyun
        print("in decide task state")
        #In this state,
        #translate the audio file('audio.wav') into text
        #save text in self.lastAudioInput

        #---------------------------------------------------------------------
        # Initialize the recognizer
        recognizer = sr.Recognizer()

        try:
            with sr.AudioFile('audio.wav') as source:
                audio = recognizer.record(source)
                # self.lastAudioInput = recognizer.recognize_google(audio)
                recognized_text = recognizer.recognize_google(audio)
                print("audio input was: ", recognized_text)
                self.lastAudioInput = recognized_text
                self.petState = 2
                return
                #return text
        #except sr.UnknownValueError:
        #    print("Speech recognition could not understand audio.")

        #NLP STUFF GOES HERE
        except:
            print("couldn't translate audio to text")
            self.lastAudioInput = "error"
            self.petState = 2
            return

        


    

    def seekMoreInfo(self, infoTitle):
        print("please provide the ",infoTitle, " for the event.")#played by the speaker
        play_response("please provide the "+infoTitle+" for the event.")
        newInfo = self.getVoiceInput()
        while newInfo == 0:
            print("didn't hear that. please provide the ",infoTitle, " for the event.")
            play_response("didn't hear that. please provide the "+infoTitle+ " for the event.")
            newInfo = self.getVoiceInput()
        return newInfo

    def getVoiceInput(self):
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
        wf.writeframes(b''.join(frames))
        wf.close()

        recognizer = sr.Recognizer()

        try:
            with sr.AudioFile('audio.wav') as source:
                audio = recognizer.record(source)
                # self.lastAudioInput = recognizer.recognize_google(audio)
                recognized_text = recognizer.recognize_google(audio)
                print("audio input was: ", recognized_text)
                return recognized_text
       

        except:
            print("couldn't translate audio to text")
            return 0

    def replyState(self):
        print("in reply state")
        recognized_text = self.lastAudioInput
        print("last audio input was: ", recognized_text)
        
        #-----------------------------------------------------------------------
        #CALENDAR SHIIIIIT
        task = categoriseText(recognized_text)
        print("task is: ", task)
        
        task = list(task)
        for i in range(len(task)):
            if len(task[i]) > 0:
                task[i] = task[i][0]
            else:
                task[i] = ""
        print("formatted task is: ", task)
        taskTitle = task[0]
        

        
        """
        1. check, plan, alarm, reminder    (p, e, w, n, m, conv)

        check -> day -> time
        plan -> day -> time -> activity
        alarm -> day -> time -> name -> occurance
        reminder -> day -> time -> name -> occurance
        gugug
        types of day: "today", "tomorrow", "yesterday", "sunday", "monday", "tuesday", "wednesday", "thursday", "friday"
        """
        if taskTitle == "check" or taskTitle == "plan" or taskTitle == "alarm" or taskTitle == "reminder":
            for i in range(len(task)):
                if i == 0:
                    continue
                elif i == 1 and task[i] == "":
                    task[i] = self.seekMoreInfo("day").lower()
                elif i == 2 and task[i] == "":
                    task[i] = self.seekMoreInfo("time")
                elif i == 3 and task[i] == "":
                    if len(task) == 4:
                        task[i] = self.seekMoreInfo("activity")
                    else:
                        task[i] = self.seekMoreInfo("name")
                elif i == 4 and task[i] == "":
                    task[i] = self.seekMoreInfo("occurance")

            if taskTitle == "check":
                print("day is:")
                print(task[1])
                print("time is:")
                print(task[2])
                result = self.calendar.check(task[1], task[2])
                print("checking calendar. result is this: ", result)
                if result == 0:
                    play_response("You have no events at this timel.")
                else:
                    play_response("You have the following event at this time. " + result.getName())
            elif taskTitle == "plan":
                result = self.calendar.plan(task[1], task[2], task[3])
                print("result when planning is this: ", result)
                if result == 0:
                    play_response("this event has been added to your calendar")
                else:
                    play_response("you already have an event at this time")
            elif taskTitle == "alarm":
                result = self.calendar.setAlarm(task[1], task[2])
                print("adding alarm. result is this: ",  result)
                if result == 0:
                    play_response("this event has been added to your calendar")
                else:
                    play_response("you already have an event at this time. This event is ")
            elif taskTitle == "reminder":
                result = self.calendar.plan(task[1], task[2], "reminder "+ task[3])
                print("adding reminder. result is this: ", result)
                if result == 0:
                    play_response("this reminder has been added to your calendar")
                else:
                    play_response("you already have an event at this time.")

            self.petState = 0
            return
        
        #------------------------------------- NEWS ------------------------------
        if taskTitle == "n":
            print("Here are the news headlines")
            print(getTopNewsHeadlines(task[1]))
            self.petState = 0
            return
        #-------------------------------------------------------------------------

        else:
            response = assistant.message(
            assistant_id=draft_environment_id,
            session_id=session_id,
            input={
                'message_type': 'text',
                'text': self.lastAudioInput
            }
            ).get_result()
            # Retrieve and print Watson Assistant's response
            try:
                response_text = response['output']['generic'][0]['text']
            except:
                print("I didn't understand. Press my button if you want to repeat yourself.")
                self.petState = 0
                return
            print("Watson Assistant: ", response_text)

        
            if(response_text == "waiting for reply"):
                self.counter = self.counter + 1
                if(self.counter > 3): #condition to move on to the seekattention state
                    self.petState = 3
                else:
                    self.petState = 1
        
    #-------------------------------------------------------------------------------------------------------------------------------------
    #News_Podcast

            elif(response_text == 'News Podcast will be played soon'):
                
                play_response(response_text)
                print("the speaker would say: ", response_text)
                #spotify_podcast_find('The News Agent', 'Lord, Ladies, and Boris Johnson honour')
                play_podcast(r"/home/pi/podcasts/News_podcast.wav")
                self.petState = 1

    #-------------------------------------------------------------------------------------------------------------------------------------
    #Comedy_Podcast

            elif(response_text == 'Comedy Podcast will be played soon'):
                
                play_response(response_text)
                print("the speaker would say: ", response_text)
                #spotify_podcast_find('Please Tell Me A Story', 'Omid: "A Fine Piece Of Ass')
                play_podcast(r"/home/pi/podcasts/Comedy_podcast.wav")
                self.petState = 1

    #-------------------------------------------------------------------------------------------------------------------------------------
    #Sports_Podcast_Tennis

            elif(response_text == 'Tennis Podcast will be played soon'):
                
                play_response(response_text)
                print("the speaker would say: ", response_text)
                #spotify_podcast_find('The Tennis Podcast', 'Roland Garros Day 14 - lga in a classic; Djokovic-Ruud preview')
                play_podcast(r"/home/pi/podcasts/Tennis_podcast.wav")
                self.petState = 1

    #-------------------------------------------------------------------------------------------------------------------------------------
    #Sports_Podcast_Cricket

            elif(response_text == 'Cricket Podcast will be played soon'):
                print("the speaker should say: ", response_text)
                play_response(response_text)
                #spotify_podcast_find('The Vaughany and Tuffers Cricket Club', 'Reflecting on an incredible year with Sam Curran')
                play_podcast(r"/home/pi/podcasts/Cricket_podcast.wav")
                self.petState = 1


    #-------------------------------------------------------------------------------------------------------------------------------------
    #Sports_Podcast_Football

            elif(response_text == 'Football will be played soon'):
            
                play_response(response_text)
                print("the speaker would say: ", response_text)
                #spotify_podcast_find('Football Daily', 'The Day After Man Citys Treble Win')
                play_podcast(r"/home/pi/podcasts/Football_podcast.wav")
                self.petState = 1

    #-------------------------------------------------------------------------------------------------------------------------------------
    #Sports_Podcast_Golf

            elif(response_text == 'Golf Podcast will be played soon'):
                
                play_response(response_text)
                print("the speaker would say: ", response_text)
                #spotify_podcast_find('Beefs Golf Club', 'The First Tee')
                play_podcast(r"/home/pi/podcasts/Golf_podcast.wav")
                self.petState = 1


    #-------------------------------------------------------------------------------------------------------------------------------------
    #Music_Podcast_Pop

            elif(response_text == 'Pop Podcast will be played soon'):
                
                play_response(response_text)
                print("the speaker would say: ", response_text)
                #spotify_podcast_find('Switched on Pop', 'Listening to Draft Punk: Random Access Memories')
                play_podcast(r"/home/pi/podcasts/Pop_music_podcast.wav")
                self.petState = 1


    #-------------------------------------------------------------------------------------------------------------------------------------
    #Music_Podcast_Classic

            elif(response_text == 'Classic Podcast will be played soon'):
                
                play_response(response_text)
                print("the speaker would say: ", response_text)
                #spotify_podcast_find('That Classic Podcast', 'So long, farewell, auf wiedersehan, goodbye!')
                play_podcast(r"/home/pi/podcasts/Classic_music_podcast.wav")
                self.petState = 1


    #-------------------------------------------------------------------------------------------------------------------------------------
    #Music_Podcast_Jazz

            elif(response_text == 'Jazz Podcast will be played soon'):
                
                play_response(response_text)
                print("the speaker would say: ", response_text)
                #spotify_podcast_find('The Jazz Session', 'The Jazz Session #617: Bill Lowe')
                play_podcast(r"/home/pi/podcasts/Jazz_music_podcast.wav")
                self.petState = 1


    #-------------------------------------------------------------------------------------------------------------------------------------
    #Music_Podcast_Rock

            elif(response_text == 'Rock Podcast will be played soon'):
                
                play_response(response_text)
                print("the speaker would say: ", response_text)
                #spotify_podcast_find('Rockonteurs with Gary Kemp and Guy Pratt', 'S4E27: Jerry Shirley')
                play_podcast(r"/home/pi/podcasts/Rock_music_podcast.wav")
                self.petState = 1

    #-------------------------------------------------------------------------------------------------------------------------------------
    #Weather
            elif(response_text == 'Checking the weather right now in London'):
                
                play_response(response_text)
                print("the speaker would say: ", response_text)
                get_weather_data()
                self.counter = 0
                self.emergency_counter = 0
                self.petState = 1

    #-------------------------------------------------------------------------------------------------------------------------------------
    #Playing_track

            elif(response_text == 'Sure, can you kindly teach me the title of the music and the name of the artist?'):

                play_response(response_text)
                print("the speaker would say: ", response_text)
                try:
                    with open('audio.wav', 'rb') as audio:
                        track_name = self.getVoiceInput().lower()
                        track_name = track_name.split(" ")
                        print("array to check perfect in is this: ", track_name)
                        if "perfect" in track_name in track_name:
                            audio = AudioSegment.from_wav('songs/Perfect by Ed Sheeran.wav')
                            play(audio)

                        elif "shape" in track_name in track_name:
                            audio = AudioSegment.from_wav('songs/Shape of you by Ed Sheeran.wav')
                            play(audio)

                        elif "blinding" in track_name in track_name:
                            audio = AudioSegment.from_wav('songs/Blinding Lights by The Weeknd.wav')
                            play(audio)

                        elif "someone" in track_name in track_name:
                            audio = AudioSegment.from_wav('songs/Someone you loved by Lewis Capaidi.wav')
                            play(audio)

                        elif "rockstar" in track_name in track_name:
                            audio = AudioSegment.from_wav('songs/Rockstar by Post Malone.wav')
                            play(audio)

                        elif "dance" in track_name in track_name:
                            audio = AudioSegment.from_wav('songs/One dance by drake.wav')
                            play(audio)

                        elif "closer" in track_name in track_name:
                            audio = AudioSegment.from_wav('songs/Closer by The Chainsmokers.wav')
                            play(audio)

                        elif "say" in track_name in track_name:
                            audio = AudioSegment.from_wav('songs/Say you won''t let go by James Arthur.wav')
                            play(audio)

                        elif "believer" in track_name in track_name:
                            audio = AudioSegment.from_wav('songs/Believer by Imagine Dragons.wav')
                            play(audio)

                        elif "rings" in track_name in track_name:
                            audio = AudioSegment.from_wav('songs/7 rigns by Ariana Grande.wav')
                            play(audio)

                        elif "bohemian" in track_name in track_name:
                            audio = AudioSegment.from_wav('songs/Bohemian Rhapsody by Queen.wav')
                            play(audio)

                        elif "watermelon" in track_name in track_name:
                            audio = AudioSegment.from_wav('songs/Watermelon sugar by Harry Styles.wav')
                            play(audio)

                        elif "photograph" in track_name in track_name:
                            audio = AudioSegment.from_wav('songs/Photograph by Ed Sheeran.wav')
                            play(audio)

                        elif "sad" in track_name in track_name:
                            audio = AudioSegment.from_wav('songs/SAD! by XXXTENTACION.wav')
                            play(audio)

                        elif "happier" in track_name in track_name:
                            audio = AudioSegment.from_wav('songs/Happier by Marshmello, Bastille.wav')
                            play(audio)
                            
                        elif "humble" in track_name in track_name:
                            audio = AudioSegment.from_wav('songs/Humble by Kendrick Lamar.wav')
                            play(audio)

                        elif "havana" in track_name in track_name:
                            audio = AudioSegment.from_wav('songs/Havana by Camila Cabello.wav')
                            play(audio)

                        elif "stay" in track_name in track_name:
                            audio = AudioSegment.from_wav('songs/Stay by The Kid LAROI, Justin Bieber.wav')
                            play(audio)

                        elif "shallow" in track_name in track_name:
                            audio = AudioSegment.from_wav('songs/Shallow by Lady Gaga, Bradley Cooper.wav')
                            play(audio)

                        elif "something" in track_name in track_name:
                            audio = AudioSegment.from_wav('songs/Something.wav')
                            play(audio)
                
                except :
                    print("Speech recognition could not understand audio.")
                self.counter = 0
                self.emergency_counter = 0
                self.petState = 0

    #-------------------------------------------------------------------------------------------------------------------------------------
    #Pausing_state

            elif(response_text == "Pausing the audio"):
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

                sp.pause_playback()
                play_response("The audio is now paused")
                print("the speaker would say: the audio is now paused")
                self.counter = 0
                self.emergency_counter = 0
                self.petState = 1
    #-------------------------------------------------------------------------------------------------------------------------------------
    #Irrelevant

            elif(response_text == 'irrelevant'):

                play_response("I am sorry could you repeat what you just said?")
                print("I am sorry could you repeat what you just said?")
                self.counter = 0
                self.emergency_counter = 0
                self.petState = 1

    #-------------------------------------------------------------------------------------------------------------------------------------
    #Termination

            elif(response_text == "Bye Bye!"):
                # End the session
                play_response(response_text)
                print("the speaker would say: ", response_text)
                self.counter = 0
                self. emergency_counter = 0

                assistant.delete_session(draft_environment_id, session_id)
                sys.exit()
                #self.petState = 1
    #-------------------------------------------------------------------------------------------------------------------------------------
            else:
                play_response(response_text)
                print("the speaker would say: ", response_text)
                self.counter = 0
                self.emergency_counter = 0
                self.petState = 1
    #-------------------------------------------------------------------------------------------------------------------------------------
    
    #def seekAttentionState(self):
    
    #    print("in seek attention state")
    #    print("I'm seeking attention")#play on speaker
    #    self.petState = 0


    def seekAttentionState(self):
        file_name = "tracklist.txt"

        print("in seek attention state")
        try:
            with open(file_name, "r") as file:
                lines = file.readlines()
                number_of_track = len(lines)
        except:
            pass


        if(self.seekattention_counter == 2):
            play_response("Everyday is a good day to listen to music, can I play a song based on your playing history?")
            print("Everyday is a good day to listen to music, can I play a song based on your playing history?")
        

            text = self.getVoiceInput().lower()
            
            if("yes" in text or "sure" in text or "go" in text):
                audio = AudioSegment.from_wav('songs/Shallow by Lady Gaga, Bradley Cooper.wav')
                play(audio)
                
                self.seekattention_counter = self.seekattention_counter + 1
                self.counter = 0
                self.petState = 1
                #try:
                #    with open(file_name, "r") as file:
                #        lines = file.readlines()
                #        random_track = random.choice(lines).strip()
                #        spotify_track_find_and_play_v2(random_track)

                #       play_random_song("/home/pi/songs")

                #        self.seekattention_counter = self.seekattention_counter + 1
                #        self.counter = 0
                #        self.trackcounter = number_of_track
                #       self.petState = 1
                #except FileNotFoundError:
                #    print("The file does not exist.")
                #    play_response("The file does not exist")
                #    self.seekattention_counter = self.seekattention_counter + 1
                #    self.counter = 0
                #    self.petState = 1
                #    pass
                #except IOError:
                #    print("An error occurred while reading the file.")
                #    play_response("An error occurred while reading the file")
                #    self.seekattention_counter = self.seekattention_counter + 1
                #    self.counter = 0
                #    self.petState = 1
                #    pass
            
            elif("no" in text or "stop" in text):
                play_response("Okay let me know if you need anything else")
                print("Okay let me know if you need anything else")
                self.seekattention_counter = self.seekattention_counter + 1
                self.counter = 0
                self.emergency_counter = 0
                self.petState = 1
            
            elif("pass" in text):
                self.seekattention_counter = self.seekattention_counter + 1
                self.emergency_counter = self.emergency_counter + 1
                self.counter = 0
                self.petState = 1
            

            else:
                play_response("I could not understand your speech. Let me know if you want me to play a music!")
                self.seekattention_counter = self.seekattention_counter + 1
                self.counter = 0
                #self.emergency_counter = self.emergency_counter + 1
                self.petState = 1



        #elif(self.trackcounter == 0 and self.seekattention_counter % 2 == 0):
        #    play_response("Let me know your taste of music! I can search a music and play it for you. Try this by just saying play me a music!")
        #    print("Let me know your taste of music! I can search a music and play it for you. Try this by just saying play me a music!")
            
            
        #    self.seekattention_counter = self.seekattention_counter + 1
        #    self.counter = 0
        #    self.petState = 1

        elif self.seekattention_counter == 0:
            sendSMS()
            randomNum = random.random()
            if randomNum < 0.5:
                #meditation task
                play_response("Meditation is a good remedy for a mental disorder. If you feel nervous I can introduce some meditation program. Do you want me to?")
                print("Meditation is a good remedy for a mental disorder. If you feel nervous I can introduce some meditation program")
                
                text = self.getVoiceInput().lower()

                if("yes" in text or "sure" in text or "go" in text):
                    #spotify_podcast_find("Meditation self", "yoga music, relaxing music, calming music")
                    play_podcast(r"/home/pi/podcasts/Meditation.wav")
                    self.seekattention_counter = self.seekattention_counter + 1
                    self.counter = 0
                    self.petState = 1
                    
                elif("no" in text or "stop" in text):
                    play_response("Okay let me know if you need anything else")
                    self.seekattention_counter = self.seekattention_counter + 1
                    self.counter = 0
                    self.petState = 1

                elif("pass" in text):
                    self.seekattention_counter = self.seekattention_counter + 1
                    self.counter = 0
                    self.emergency_counter = self.emergency_counter + 1
                    self.petState = 1

                else:
                    play_response("I could not understand your speech. If you want me to play a medication podcast, just say it to me!")
                    self.seekattention_counter = self.seekattention_counter + 1
                    self.counter = 0
                    self.petState = 1
                #pass
            else:
                #exercise task
                play_response("Did you know that regular exercise can decrease the heart attack rate by 80 percent? If you need any help to start an exercise, I can play a tutorial for you. Do you want me to play it?")
                print("Did you know that regular exercise can decrease the heart attack rate by 80 percent? If you need any help to start an exercise, I can play a tutorial for you. Do you want me to play it?")
                text = self.getVoiceInput()

                if("yes" in text or "sure" in text or "go" in text):
                    #spotify_podcast_find("Meditation self", "yoga music, relaxing music, calming music")
                    play_podcast(r"/home/pi/podcasts/exercise_tutorial.wav")
                    self.seekattention_counter = self.seekattention_counter + 1
                    self.counter = 0
                    self.petState = 1
                    
                elif("no" in text or "stop" in text or "I am okay"):
                    play_response("Okay let me know if you need anything else")
                    self.seekattention_counter = self.seekattention_counter + 1
                    self.counter = 0
                    self.petState = 1

                elif("pass" in text):
                    self.seekattention_counter = self.seekattention_counter + 1
                    self.counter = 0
                    self.emergency_counter = self.emergency_counter + 1
                    self.petState = 1

                else:
                    play_response("I could not understand your speech. If you want me to play a exercise tutorial, just say it to me!")
                    self.seekattention_counter = self.seekattention_counter + 1
                    self.counter = 0
                    self.petState = 1
                #pass

        #-------------------------------------------------------------------------------------------------------------------------------------
        #Emergency state
        elif(self.emergency_counter > 4):
            print("Are you okay? If don't respond to this I am assuming you are in danger and I am asking for some help to your Whatsapp friend")
            # sendSMS(self.username, self.contactNumber)
            sys.exit()
        
        #-------------------------------------------------------------------------------------------------------------------------------------
        
        else:
            play_response("Hello, where are you?")
            print("Hello where are you?")
            self.seekattention_counter = self.seekattention_counter + 1
            self.counter = 0
            self.petState = 1


    def alarmState(self):
        print("in alarm state")
        time.sleep(3)
        play_response(self.alarmSound)
        time.sleep(1)
        self.petState = 0


    def run(self):
        while(True):
            if self.petState == 0:
                self.idleState()
            if self.petState == 1:
                self.listenState()
            if self.petState == 2:
                self.replyState()
            if self.petState == 3:
                self.seekAttentionState()
            if self.petState == 4:
                self.alarmState()



def __main__():
   
    pet = Pet()

    app = Flask(__name__)
    def run_flask_app():
        time.sleep(1)
        app.run(host='0.0.0.0', port=5000, debug=False)
    
    @app.route('/data', methods=['POST'])
    def receive_data():
            print("check")
            data = request.json
            name = data.get('name')
            print('Received data:', data)
            pet.userName = data.get('name')
            pet.emailAddress = data.get('email')
            pet.location = data.get('location')
            pet.animalType = data.get('animal')
            pet.spUsername = data.get('spotify username')
            pet.spPassword = data.get('spotify password')
            pet.contactNumber = data.get('contact')   
            return "Data received"
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()
    pet.run()

__main__()
