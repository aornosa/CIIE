"""
scenes/game_scene.py  —  LEGACY, NO USAR
-----------------------------------------
Este archivo existía como wrapper de game.py (sistema de juego antiguo).
El flujo actual es:  MainMenuScene  →  Level1Scene

Si ves este import en algún archivo, cámbialo por Level1Scene.
"""

raise ImportError(
    "game_scene.py es código legacy y ya no está en uso. "
    "Usa 'from scenes.level1_scene import Level1Scene' en su lugar."
)