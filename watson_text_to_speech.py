from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import pyaudio
import wave
import pydub
import simpleaudio

# Set up the Text to Speech service
apikey = 'RL8bEBwfNsNhJ8uzZWGVWIWKZi_sIe2eptFqcGdytYXH'
url = 'https://api.au-syd.text-to-speech.watson.cloud.ibm.com/instances/5da2b1e5-0bde-4a8c-bd7a-ebb249bb968b'
authenticator = IAMAuthenticator(apikey)
text_to_speech = TextToSpeechV1(authenticator=authenticator)
text_to_speech.set_service_url(url)

def convert_text_to_speech():

    text = "Hi, where are you?"
    output_file = "output.wav"
    try:
        # Perform text to speech conversion
        response = text_to_speech.synthesize(text, accept='audio/wav', voice='en-US_AllisonV3Voice').get_result()

        # Save the audio to a file
        with open(output_file, 'wb') as audio_file:
            audio_file.write(response.content)

        print("Text to Speech conversion completed.")
        # Load the audio file
        audio = pydub.AudioSegment.from_wav(output_file)

        # Play the audio
        play_obj = simpleaudio.play_buffer(audio.raw_data, num_channels=audio.channels, bytes_per_sample=audio.sample_width, sample_rate=audio.frame_rate)
        play_obj.wait_done()

    except Exception as e:
        print("Error converting text to speech:", str(e))

#text = "Hello, how are you?"
#output_file = "output.wav"

convert_text_to_speech()