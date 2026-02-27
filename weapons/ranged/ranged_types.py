from weapons.ranged.ranged import Ranged

class AK47(Ranged):
    def __init__(self):
        super().__init__(
            asset="assets/weapons/AK47.png",
            name="AK-47",
            damage=60,
            max_range=1500,
            ammo_type="7.62",
            clip_size=30,
            fire_rate=0.1,
            reload_time=2,
            muzzle_offset=(35, 15)
        )

class MP5(Ranged):
    def __init__(self):
        super().__init__(
            asset="assets/weapons/mp5/mp5.png",
            name="MP5",
            damage=18,
            max_range=800,
            ammo_type="9x19",
            clip_size=30,
            fire_rate=0.10,
            reload_time=2.0,
            muzzle_offset=(35, 15)
        )


class SPAS12(Ranged):
    def __init__(self):
        super().__init__(
            asset="assets/weapons/spas12/spas12.png",
            name="SPAS-12",
            damage=80,
            max_range=400,
            ammo_type="12gauge",
            clip_size=8,
            fire_rate=0.833,
            reload_time=3.0,
            muzzle_offset=(35, 15)
        )