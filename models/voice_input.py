"""voice_input.py — AI Feature 4: Speech Recognition Voice Input"""

class VoiceInput:
    LANG_CODES = {"en":"en-IN","hi":"hi-IN","kn":"kn-IN"}

    def __init__(self):
        import speech_recognition as sr
        self.r = sr.Recognizer()

    def listen(self, lang="en", timeout=6) -> str:
        import speech_recognition as sr
        with sr.Microphone() as src:
            self.r.adjust_for_ambient_noise(src, duration=0.5)
            audio = self.r.listen(src, timeout=timeout, phrase_time_limit=12)
        return self.r.recognize_google(audio, language=self.LANG_CODES.get(lang,"en-IN"))

    def process_text(self, text: str) -> list:
        fillers = ["i have","and","also","with","some","the","a","an","plus","along with"]
        t = text.lower()
        for f in fillers: t = t.replace(f, ",")
        return [i.strip() for i in t.split(",") if i.strip() and len(i.strip()) > 1]
