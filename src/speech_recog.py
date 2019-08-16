#!/usr/bin/env python
#-*- coding: utf-8 -*-

# [START transcribe]
from __future__ import division

import re
import sys

# [prameter]------------------->
IS_ROS_ACTIVE = True
# <-----------------------------
if IS_ROS_ACTIVE:
    import rospy
    from std_msgs.msg import String,Bool
    from ti_gpsr.msg import array

import Levenshtein as lev

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import pyaudio
from six.moves import queue

# 言語処理
import lp_gogetit

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE // 10)  # 100ms

End_flug = False
google_start_sub = False


class MicrophoneStream(object):
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )
        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)

class CallApi(object):
    def __init__(self):
        rospy.init_node('gogetit_speech_recog')
        rospy.loginfo("Init_node 'gogetit_speech_recog' ")

        # ROS Subscriber
        self.follow_start_sub = rospy.Subscriber('/ggi/training_request', String, self.Follow_ApiStartCB)
        self.train_start_sub = rospy.Subscriber('/ggi/learn_request', String, self.Train_ApiStartCB)
        self.task_start_sub = rospy.Subscriber('/ggi/mission_listen', String, self.Task_ApiStartCB)
        # ROS Publisher
        self.tts_pub = rospy.Publisher('/tts', String, queue_size = 1)
        self.follow_stop_pub = rospy.Publisher('/ggi/voice_cmd', String, queue_size = 1)
        self.train_result_pub = rospy.Publisher('/ggi/learn_content', String, queue_size = 1)
        self.send_action_pub = rospy.Publisher('/ggi/order_content', String, queue_size = 1)

        self.followstart = "False"
        self.trainstart = "False"
        self.taskstart = "False"

    def Follow_ApiStartCB(self, msg):
        self.followstart = msg.data

    def Train_ApiStartCB(self, msg):
        self.trainstart = msg.data

    def Task_ApiStartCB(self, msg):
        self.taskstart = msg.data

    def listen_print_loop(self, responses):
        num_chars_printed = 0
        for response in responses:
            if not response.results:
                continue

            # The `results` list is consecutive. For streaming, we only care about
            # the first result being considered, since once it's `is_final`, it
            # moves on to considering the next utterance.
            result = response.results[0]
            if not result.alternatives:
                continue

            # Display the transcription of the top alternative.
            transcript = result.alternatives[0].transcript

            # Display interim results, but with a carriage return at the end of the
            # line, so subsequent lines will overwrite them.
            #
            # If the previous result was longer than this one, we need to print
            # some extra spaces to overwrite the previous result
            overwrite_chars = ' ' * (num_chars_printed - len(transcript))

            if not result.is_final:
                sys.stdout.write(transcript + overwrite_chars + '\r')
                sys.stdout.flush()

                num_chars_printed = len(transcript)

            else:
                print(transcript + overwrite_chars)
                break

                # Exit recognition if any of the transcribed phrases could be
                # one of our keywords.
                if re.search(r'\b(exit|quit)\b', transcript, re.I):
                    print('Exiting..')
                    break

                num_chars_printed = 0

        return transcript + overwrite_chars

    def google_speech_api(self):
        # See http://g.co/cloud/speech/docs/languages
        # for a list of supported languages.
        language_code = 'en-US'  # a BCP-47 language tag

        client = speech.SpeechClient()
        config = types.RecognitionConfig(
            encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code=language_code)
        streaming_config = types.StreamingRecognitionConfig(
            config=config,
            interim_results=True)

        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (types.StreamingRecognizeRequest(audio_content=content)
                        for content in audio_generator)

            responses = client.streaming_recognize(streaming_config, requests)

            # Now, put the transcription responses to use.
            sentence = self.listen_print_loop(responses)

        return sentence


    def FollowCmdLoop(self):
        cmd_list = ["follow me", "stop follow", "turn right", "turn left", "go back", "start learning",]
        flug = True
        while flug:
            sentence = self.google_speech_api()
            distance_max = 0.0
            result_str = "str"
            for i in cmd_list:
                distance = lev.ratio(i, sentence)*1.00
                if distance_max <= distance:
                    distance_max = distance
                    result_str = i

            if distance_max == 0.8:
                self.follow_stop_pub.publish(resutl_str)
                flug = False


    def TrainingLoop(self):
        a = lp_gogetit.Training()
        object_key = "this is"
        location_key = "there is"
        feature_key = "it is"

        self.tts_pub.publish("Please tell me a location name")
        rospy.sleep(3)
        a.TrainingConversation("object", "object name", object_key)
        a.TrainingConversation("location", "location name", location_key)

        while 1:
            a.TrainingConversation("feature", "feature", feature_key)


        self.tts_pub.publish("Please tell me a object name")
        self.tts_pub.publish("Please tell me the features")



    def TestPhaseLoop(self):
        sentence_list = ["bring me the {object} from the {location}", "bring me the {object}", "bring me a {object} near the standing person", "Bring me a {feature} object in front of the {location}"]
        sentence = self.google_speech_api()
        for i in sentence_list:
            distance = lev.ratio(i, sentence)*1.00
            if distance_max <= distance and distance >= 0.4:
                distance_max = distance_max


    def MainLoop(self):
        follow_flug = True
        self.training_flug == True
        while not rospy.is_shutdown():
            if training_flug:
                if follow_flug:
                    if self.followstart == "start":
                        self.FollowCmdLoop()
                        follow_flug = False

                    else:
                        rospy.loginfo("Wating for '/ggi/training_request' topic...")
                        rospy.sleep(1.5)

                else:
                    if self.trainstart == "start":
                        self.TrainingLoop()
                        if self.training_flug:
                            follow_flug = True

                    else:
                        rospy.loginfo("Wating for '/ggi/learn_request' topic...")
                        rospy.sleep(1.5)

            else:
                if self.taskstart == "start":
                    self.TestPhaseLoop()

                else:
                    rospy.loginfo("Waiting for '/ggi/mission_listen' topic...")
                    rospy.sleep(1.5)




if __name__ == '__main__':
    call = CallApi()
    call.MainLoop()

# [END transcribe]
