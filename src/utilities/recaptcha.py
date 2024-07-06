# forked from: https://github.com/sarperavci/GoogleRecaptchaBypass
# modified to use selenium instead of DrissionPage
# As of v1.0.3 Increased Captcha solver speed by 29.58% - 35.16%

# extractToken() was forked from https://github.com/MachineKillin/Ciper

import os
import urllib
import random
import pydub
import speech_recognition
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import urlparse
from utilities.colored import print_green, print_red

class RecaptchaSolver:
    def __init__(self, driver: webdriver.Chrome, thread_id:str):
        self.driver: webdriver.Chrome = driver
        self.thread_id: str = thread_id
    
    def extractToken(self) -> str:
        try:
            abuseExceptionToken = self.driver.get_cookie('GOOGLE_ABUSE_EXEMPTION')['value']
            bypass = abuseExceptionToken
        except Exception:
            url = str(urlparse(self.driver.current_url))
            token = str(re.findall("(?<=GOOGLE_ABUSE_EXEMPTION=).+?(?=; path=/;)", url)).replace("['", "").replace("']", "")
            token = token
            bypass = token
        return bypass
    
    def solveCaptcha(self) -> bool:
        time.sleep(random.uniform(3, 4))
        
        # Switch to the reCAPTCHA iframe
        iframe_inner = self.driver.execute_script('return document.getElementsByTagName("iframe")[0]')
        self.driver.switch_to.frame(iframe_inner)
        time.sleep(random.uniform(1, 2))
        
        # Click on the reCAPTCHA
        recaptcha_checkbox = WebDriverWait(self.driver, 7).until(
            EC.element_to_be_clickable((By.CLASS_NAME, 'rc-anchor-content'))
        )
        recaptcha_checkbox.click()
        self.driver.switch_to.default_content()
        
        time.sleep(random.uniform(4, 5))  # wait for reCAPTCHA to load

        # Check if the reCAPTCHA is solved
        if self.isSolved():
            print_green("Captcha Solved!")
            return True
        
        # Switch to the new iframe
        iframe = self.driver.execute_script('return document.getElementsByTagName("iframe")[2]')
        self.driver.switch_to.frame(iframe)

        enable_audio_button = "var element = document.getElementById('recaptcha-audio-button'); element.disabled = false; element.classList.remove('rc-button-disabled');"

        self.driver.execute_script(enable_audio_button)
        time.sleep(random.uniform(3, 5))
        
        # Click on the audio button
        audio_button = WebDriverWait(self.driver, 7).until(
            EC.element_to_be_clickable((By.ID, 'recaptcha-audio-button'))
        )
        audio_button.click()
        time.sleep(3)
        
        if self.isIPBlocked():
            raise Exception(f"[{self.thread_id}]: IP block detected, swapping proxies.")
        
        # Get the audio source
        audio_source = WebDriverWait(self.driver, 5).until(
           EC.presence_of_element_located((By.ID, 'audio-source'))
        )
        src = audio_source.get_attribute('src')

        # Define the temporary directory based on the operating system
        temp_dir = os.getenv("TEMP") if os.name == "nt" else "/tmp/"

        # Generate random file names for the mp3 and wav files
        path_to_mp3 = os.path.normpath(os.path.join(temp_dir, f"{random.randrange(1, 1000)}.mp3"))
        path_to_wav = os.path.normpath(os.path.join(temp_dir, f"{random.randrange(1, 1000)}.wav"))

        # Download the audio to the temp folder
        urllib.request.urlretrieve(src, path_to_mp3)

        # Convert mp3 to wav
        sound = pydub.AudioSegment.from_mp3(path_to_mp3)
        sound.export(path_to_wav, format="wav")
        sample_audio = speech_recognition.AudioFile(path_to_wav)
        r = speech_recognition.Recognizer()
        with sample_audio as source:
            audio = r.record(source)
        
        # Recognize the audio
        key = r.recognize_google(audio)
        
        # Input the key
        audio_response_input = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.ID, 'audio-response'))
        )
        audio_response_input.send_keys(key.lower())
        time.sleep(random.uniform(2, 4))
        
        # Submit the key
        audio_response_input.send_keys(Keys.ENTER)
        time.sleep(random.uniform(3, 5))

        # Switch back to default content
        self.driver.switch_to.default_content()

        # Check if the captcha is solved
        if self.isSolved():
            print_green(f"[{self.thread_id}]: Captcha solved!")
            token = self.extractToken()
            self.driver.add_cookie({'name': 'GOOGLE_ABUSE_EXEMPTION', 'value': token})
            #print(self.driver.get_cookie("GOOGLE_ABUSE_EXEMPTION"))
            return True
        else:
            print_red(f"[{self.thread_id}]: Failed to solve captcha.")
            return False

    def isSolved(self) -> bool:
        try:
            if "https://www.google.com/search?" in self.driver.current_url:
                return True
            
            # Check if the recaptcha checkbox has the 'recaptcha-checkbox-checked' class
            self.driver.switch_to.default_content()
            checkbox = self.driver.find_element(By.CLASS_NAME, 'recaptcha-checkbox-checkmark')
            return checkbox.is_displayed()
        except Exception:
            return False
    
    def isIPBlocked(self) -> bool:
        try:
            ip_block = "Your computer or network may be sending automated queries. To protect our users, we can't process your request right now."
            return ip_block in self.driver.execute_script("return document.documentElement.innerHTML;")
        except Exception:
            return False
