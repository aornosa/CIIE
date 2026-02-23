from core.audio.audio_clip import AudioClip
from core.audio.audio_mixer_category import SoundCategory

# Init cache. Not very scalable, works here.
SOUNDS = {
    # PLAYER
    "player_hurt": AudioClip("assets/player/sfx/hurt.wav", priority=0),
    "player_death": AudioClip("assets/player/sfx/death.wav", priority=0),

    # ZOMBIE
    "zombie_groan": AudioClip("assets/zombie/sfx/groan.wav", priority=2),
    "zombie_hurt": AudioClip("assets/zombie/sfx/hurt.wav", priority=1),
    "zombie_death": AudioClip("assets/zombie/sfx/death.wav", priority=1),

    # AMMO
    # 9x19
    "9mm_shoot": AudioClip("assets/ammo/9x19/sfx/shoot.wav", priority=0),
    "9mm_reload": AudioClip("assets/ammo/9x19/sfx/reload.wav", priority=0),

    # 7.62
    "7.62mm_shoot": AudioClip("assets/ammo/7.62/sfx/shoot.wav", priority=0),
    "7.62mm_reload": AudioClip("assets/ammo/7.62/sfx/reload.wav", priority=0),

    # 12 gauge
    "12gauge_shoot":   AudioClip("assets/ammo/12gauge/sfx/shoot.wav",priority=0),
    "12gauge_reload":  AudioClip("assets/ammo/12gauge/sfx/reload.wav",priority=0),

    # Other
    "dry_fire": AudioClip("assets/ammo/other/sfx/dry_fire.wav", priority=1),

    # CONSUMABLES
    "injector_use": AudioClip("assets/items/phoenix_injector/sfx/use.wav", priority=0),

    # UI
    "ui_click": AudioClip("assets/ui/sfx/click.wav", priority=0, category=SoundCategory.UI),
}
