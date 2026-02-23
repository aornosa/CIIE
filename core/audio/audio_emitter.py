class AudioEmitter:
    def __init__(self, position, audio_clip, loop=False):
        self.position = position
        self.audio_clip = audio_clip
        self.loop = loop
        self.channel = None
        self.max_distance = 500  # Max distance for sound attenuation

    def set_position(self, position):
        self.position = position

    def get_position(self):
        return self.position


    def play(self):
        if self.channel is None or not self.channel.get_busy():
            loops = -1 if self.loop else 0
            self.channel = self.audio_clip.source.play(loops=loops)

    def stop(self):
        if self.channel is not None:
            self.channel.stop()