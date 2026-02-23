from core.audio.audio_manager import AudioManager
from core.monolite_behaviour import MonoliteBehaviour


class AudioEmitter(MonoliteBehaviour):
    def __init__(self, owner, position, audio_clip, loop=False):
        MonoliteBehaviour.__init__(self)
        self.owner = owner
        self.position = position
        self.audio_clip = audio_clip
        self.loop = loop
        self.channel = None
        self.max_distance = 500  # Max distance for sound attenuation

    def set_position(self, position):
        self.position = position

    def get_position(self):
        return self.position

    def sync_with_owner(self):
        if self.owner is not None:
            self.position = self.owner.get_position()

    def play(self):
        AudioManager.instance().play_sound(self.audio_clip, self)

    def stop(self):
        if self.channel is not None:
            self.channel.stop()

    def update(self):
        self.sync_with_owner()