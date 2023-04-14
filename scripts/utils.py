from telegram_chat import TelegramUtils
import speech_recognition as sr
import speak
import traceback
import asyncio

from config import Config
cfg = Config()


def voice_input(prompt: str = "", voice_prompt_counter: int = 0):
    recognizer = sr.Recognizer()

    if voice_prompt_counter > 3:
        speak.macos_tts_speech(
            "I'm sorry, I didn't understand that. Please use the keyboard.")
        return clean_input(prompt, talk=False)

    voice_prompt_counter += 1
    try:
        speak.macos_tts_speech(prompt)
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
        try:
            user_input = recognizer.recognize_sphinx(audio)

            if user_input in ["yes", "yeah", "yep", "yup", "y", "ok", "okay", "sure", "affirmative", "aye", "aye aye", "alright", "alrighty"]:
                return "y"
            elif user_input in ["no", "nope", "n", "nah", "negative", "nay", "nay nay"]:
                return "n"
            elif user_input in ["quit", "exit", "stop", "end", "terminate", "cancel", "break", "halt", "die", "kill", "terminate"]:
                speak.macos_tts_speech("Okay then.. Goodbye!")
                print("You interrupted Auto-GPT")
                print("Quitting...")
                exit(0)
            elif user_input in ["do what you want", "keep going", "keep on going", "keep on"]:
                return "y -15"
            else:
                print("You said: " + user_input)
                return input(prompt)

        except sr.UnknownValueError:
            print(traceback.format_exc())
            print("Siri could not understand your input.")
            speak.macos_tts_speech("I didn't understand that. Sorry.")
            return input(prompt)
    except KeyboardInterrupt:
        print("You interrupted Auto-GPT")
        print("Quitting...")
        exit(0)


def clean_input(prompt: str = '', talk=False):
    try:
        if talk and cfg.use_mac_os_voice_input == 'True':
            try:
                return voice_input(prompt)
            except:
                print(traceback.format_exc())
                print("Siri could not understand your input.")
                speak.macos_tts_speech("I didn't understand that. Sorry.")
                return input(prompt)
        else:
            if cfg.telegram_enabled:
                print("Asking user via Telegram...")
                chat_answer = asyncio.run(TelegramUtils.ask_user(prompt))
                print("Telegram answer: " + chat_answer)
                if chat_answer in ["yes", "yeah", "yep", "yup", "y", "ok", "okay", "sure", "affirmative", "aye", "aye aye", "alright", "alrighty"]:
                    return "y"
                elif chat_answer in ["no", "nope", "n", "nah", "negative", "nay", "nay nay"]:
                    return "n"
                      
            ## ask for input, default when just pressing Enter is y
            print("Asking user via keyboard...")
            answer = input(prompt + ' [y/n] or press Enter for default (y): ')
            if answer == '':
                answer = 'y'
            return answer
    except KeyboardInterrupt:
        print("You interrupted Auto-GPT from utils.py")
        print("Quitting...")
        print(traceback.format_exc())
        exit(0)
