from weapons.ranged.ranged import Ranged

class AK47(Ranged):
    def __init__(self):
        super().__init__(
            asset="assets/weapons/AK47.png",
            name="AK-47",
            damage=75,
            max_range=1500,
            ammo_type="7.62",
            clip_size=45,
            fire_rate=0.20,
            reload_time=1.8,
            muzzle_offset=(35, 15),
        )

class MP5(Ranged):
    def __init__(self):
        super().__init__(
            asset="assets/weapons/mp5/mp5.png",
            name="MP5",
            damage=22,
            max_range=600,
            ammo_type="9x19",
            clip_size=60,
            fire_rate=0.09,
            reload_time=1.4,
            muzzle_offset=(35, 15),
        )

class SPAS12(Ranged):
    def __init__(self):
        super().__init__(
            asset="assets/weapons/spas12/spas12.png",
            name="SPAS-12",
            damage=160,
            max_range=250,
            ammo_type="12gauge",
            clip_size=15,
            fire_rate=0.7,
            reload_time=2.0,
            muzzle_offset=(35, 15),
        )