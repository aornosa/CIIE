import pygame
pygame.init()
assets = [
    ("red.png/TankEnemy scale=0.15",     "assets/enemies/red.png",    0.15),
    ("green.png/ToxicEnemy scale=0.12",  "assets/enemies/green.png",  0.12),
    ("yellow.png/ShooterEnemy scale=0.10","assets/enemies/yellow.png", 0.10),
    ("infected_common scale=0.20",        "assets/enemies/infected_common/infected_common.png", 0.20),
]
for name, path, scale in assets:
    try:
        img = pygame.image.load(path)
        w, h = img.get_size()
        cw = int(w * scale) // 2
        ch = int(h * scale) // 2
        print(f"{name}: imagen {w}x{h} → collider {cw*2}x{ch*2}px (radio ~{max(cw,ch)}px)")
    except Exception as e:
        print(f"{name}: ERROR {e}")
