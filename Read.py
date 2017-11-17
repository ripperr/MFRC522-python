#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import time

import MFRC522
import signal
import urllib2
import urllib

COOLDOWN_SECONDS = 10

URL = "http://localhost:8080"
COOLDOWN_TIME_ = 0.0
BLOCKED_UUID_ = ""

continue_reading = True


# Capture SIGINT for cleanup when the script is aborted
def end_read(signal, frame):
    global continue_reading
    print("Ctrl+C captured, ending read.")
    continue_reading = False
    GPIO.cleanup()


# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)

# Create an object of the class MFRC522
MIFAREReader = MFRC522.MFRC522()

# Welcome message
print("Welcome to the MFRC522 data read example")
print("Press Ctrl-C to stop.")


def create_uuid():
    return str(uid[0]) + "," + str(uid[1]) + "," + str(uid[2]) + "," + str(uid[3])


def build_url():
    return URL


def get_post_parameters():
    data_to_post = {'deviceId': 1, 'rfidTag': uuid}
    return urllib.urlencode(data_to_post)


def call_backend():
    global COOLDOWN_TIME_, BLOCKED_UUID_
    COOLDOWN_TIME_ = time_since_epoch
    BLOCKED_UUID_ = uuid
    data_to_post = get_post_parameters()
    print("Calling url: " + uuid_url)
    urllib2.Request(uuid_url, data_to_post)


# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:

    # Scan for cards
    (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)

    # If a card is found
    if status == MIFAREReader.MI_OK:
        print("Card detected")

    # Get the UID of the card
    (status, uid) = MIFAREReader.MFRC522_Anticoll()

    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:
        uuid = create_uuid()
        # Print UID
        print("Card read UID: " + uuid)

        time_since_epoch = int(time.time())
        difference_in_time = time_since_epoch - COOLDOWN_TIME_
        uuid_url = build_url()
        try:
            if (difference_in_time > COOLDOWN_SECONDS) or (uuid != BLOCKED_UUID_):
                print("Seconds since latest logon: " + str((time_since_epoch - COOLDOWN_TIME_)))
                call_backend()
            else:
                print("In cooldown time... " + str(COOLDOWN_SECONDS - difference_in_time) + " seconds remaining")
        except Exception:
            print("Can't call url: " + uuid_url)

        # This is the default key for authentication
        key = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)

        # Authenticate
        status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

        # Check if authenticated
        if status == MIFAREReader.MI_OK:
            MIFAREReader.MFRC522_Read(8)
            MIFAREReader.MFRC522_StopCrypto1()
        else:
            print("Authentication error")
