#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
import time

import MFRC522
import signal
import urllib2

COOLDOWN_SECONDS = 10

HTTP_LOCALHOST_ = "http://localhost:8080"
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
        if (difference_in_time > COOLDOWN_SECONDS) or (uuid != BLOCKED_UUID_):

            print("time since epoch: " + str(time_since_epoch))
            print("cooldown time: " + str(COOLDOWN_TIME_))
            print("difference: " + str((time_since_epoch - COOLDOWN_TIME_)))
            quoted_uuid_string = urllib2.quote(uuid)
            uuid_url = HTTP_LOCALHOST_ + "?rfid=" + quoted_uuid_string
            print(uuid_url)
            COOLDOWN_TIME_ = time_since_epoch
            BLOCKED_UUID_ = uuid
            urllib2.Request(uuid_url)
        else:
            print("In cooldown time... " + str(COOLDOWN_SECONDS - difference_in_time) + " seconds remaining")
        try:
            print("meuh")
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
