"""
Singleton container for game data that must persist across levels.
Player stats, inventory, coins, etc. survive when switching levels.

Usage:
    from runtime.persistent_data import GameState

    player = GameState.get_player()
    controller = GameState.get_controller()
"""


class GameState:
    _player = None
    _controller = None

    @classmethod
    def get_player(cls):
        """Return the shared Player, creating it on first call."""
        if cls._player is None:
            cls._init_systems()

            from character_scripts.player.player import Player
            cls._player = Player(
                "assets/player/survivor-idle_rifle_0.png", (0.0, 0.0)
            )
        return cls._player

    @classmethod
    def get_controller(cls):
        """Return the shared CharacterController."""
        if cls._controller is None:
            from character_scripts.character_controller import CharacterController
            cls._controller = CharacterController(250, cls.get_player())
        return cls._controller

    @classmethod
    def reset(cls):
        """Full reset — call when starting a new game from scratch."""
        cls._player = None
        cls._controller = None

    # ── internal helpers ──────────────────────────────────────

    @classmethod
    def _init_systems(cls):
        """Ensure core singletons (CollisionManager, AudioManager,
        ItemRegistry) exist before any game object is created."""
        from core.collision.collision_manager import CollisionManager
        from core.collision.quadtree import Rectangle
        from core.audio.audio_manager import AudioManager
        from item.item_loader import ItemRegistry

        # CollisionManager
        if CollisionManager._active is None:
            world_bounds = Rectangle(-4000, -4000, 8000, 8000)
            CollisionManager(world_bounds)

        # AudioManager
        if AudioManager._instance is None:
            AudioManager._instance = AudioManager()

        # ItemRegistry (items are stored on the class; only load once)
        if not ItemRegistry._items:
            ItemRegistry()
            ItemRegistry.load("assets/items/item_data.json")
