#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os

import xml.etree.ElementTree as ET


class Training(object):
    def __init__(self):
        path = os.path.abspaht("/home/rei/catkin_ws/src/gogetit/resource/CommonFiles")
        Obj_root = ET.parse(os.path.join(path, "Objects.xml")).getroot()
        Loc_root = ET.parse(os.path.join(path, "Locations.xml")).getroot()

        self.ObjectData_word_list_nb = []
        self.LocationData_word_list_nb = []

        for i in self.Obj_root:
            for obj in i:
                self.ObjectData_word_list_nb.append(obj.get("name"))

        for i in Loc_root:
            for loc in i:
                self.LocationData_word_list_nb.append(loc.get("name"))


    def TrainingConversation(self, content ,name, key):
        if content == "object":
            list = self.ObjectData_word_list_nb
        elif content == "location":
            list = self.LocationData_word_list_nb
        else:
            list = [""]

        self.tts_pub.publish("Please tell me a "+ name)
        rospy.sleep(3)
        while flug:
            sentence = self.google_speech_api()

            self.tts_pub.publish("you say " + answer + ". OK?")
            rospy.sleep(3)
            answer = self.google_speech_api()
            if lev.ratio(answer, "OK")*1.00 >= 0.7:
                self.tts_pub.publish("ok. save a " + name)
                rospy.sleep(3)
                location_flug = False
            else:
                self.tts_pub.publish("please tell me a " + name + " again")
                rospy.sleep(3)


class Task(object):
    def
