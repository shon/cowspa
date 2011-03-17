import base64, random, hashlib

random_key_gen = None

class odict(dict):
    def __getattr__(self, attr):
        return self[attr]

class RandomKeyFactory(object):
    def __init__(self, s):
        self.random_choices = (s[:2], s[2:4], s[4:6], s[6:8], s[8:10], s[10:12], s[12:14])
    def __call__(self):
        return base64.b64encode(hashlib.sha256(str(random.getrandbits(256))).digest(), \
            random.choice(self.random_choices)).rstrip('==')
