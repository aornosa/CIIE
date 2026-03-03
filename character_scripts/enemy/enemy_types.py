from character_scripts.enemy.enemy_base import Enemy


class InfectedCommon(Enemy):
    """
    Civil infectado de las ruinas de Trinitas.
    Ropa destrozada, movimiento errático. Peligroso en grupos.
    - Bajo HP, bajo daño, velocidad media
    - Ataca en melee cuerpo a cuerpo
    """
    ATTACK_RANGE = 45       
    DETECTION_RANGE = 300   
    ATTACK_COOLDOWN = 1.2   

    def __init__(self, position=(0, 0)):
        super().__init__(
            asset="assets/enemies/infected_common/infected_common.png",
            position=position,
            name="Infectado",
            health=60,
            strength=12,
            speed=90,
        )
        self._attack_timer = 0.0

    def can_attack(self, delta_time):
        self._attack_timer += delta_time
        if self._attack_timer >= self.ATTACK_COOLDOWN:
            self._attack_timer = 0.0
            return True
        return False


class InfectedSoldier(Enemy):
    """
    Exsoldado AdNBQ infectado. Lleva restos de equipo táctico.
    Más resistente y dañino. Compañeros caídos de Adrian reanimados.
    - HP medio-alto, daño alto, velocidad media-baja (armadura pesada)
    - Ataca en melee, puede aguantar más antes de caer
    """
    ATTACK_RANGE = 55
    DETECTION_RANGE = 400
    ATTACK_COOLDOWN = 1.8

    def __init__(self, position=(0, 0)):
        super().__init__(
            asset="assets/enemies/infected_soldier/infected_soldier.png",
            position=position,
            name="Soldado Infectado",
            health=150,
            strength=28,
            speed=70,
        )
        self._attack_timer = 0.0

    def can_attack(self, delta_time):
        self._attack_timer += delta_time
        if self._attack_timer >= self.ATTACK_COOLDOWN:
            self._attack_timer = 0.0
            return True
        return False


class LabSubject(Enemy):
    """
    Sujeto de experimentación del Laboratorio Armengard.
    Cuerpo distorsionado por las pruebas de resistencia biológica.
    Exclusivo del segundo acto (laboratorio).
    - Muy alto HP, daño devastador, muy lento
    - Actúa como mini-boss de sala
    """
    ATTACK_RANGE = 70
    DETECTION_RANGE = 250   
    ATTACK_COOLDOWN = 2.5

    def __init__(self, position=(0, 0)):
        super().__init__(
            asset="assets/enemies/lab_subject/lab_subject.png",
            position=position,
            name="Sujeto de Laboratorio",
            health=320,
            strength=55,
            speed=45,
        )
        self._attack_timer = 0.0

    def can_attack(self, delta_time):
        self._attack_timer += delta_time
        if self._attack_timer >= self.ATTACK_COOLDOWN:
            self._attack_timer = 0.0
            return True
        return False