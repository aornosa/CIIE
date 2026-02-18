# Developer Manual: Collisions
As per almost any game engine requires, we implemented a `Collision` system that allows for detecting 
overlapping objects and responding to those collisions. We based the implementation around the concept
of **[Quadtrees](https://en.wikipedia.org/wiki/Quadtree)**, which divides world space on demand.

## Collider
The `Collider` class is a component that can be attached to any game object to enable collision detection. It
contains a `pygame.Rect` that defines the area of the collider, which by default is the same as the object's
asset.

### Attributes
- `owner`: The game object, or parent, that owns this collider.
- `rect`: A `pygame.Rect` that defines the area of the collider. By default, it is set to match the dimensions
    of the owner's asset, but it can be customized to fit specific needs.
- `layer`: An integer that represents the collision layer for filtering. (I.E. PlayerLayer=0, EnemyLayer=1, etc.)
- `tag`: A string that can be used to identify the collider for specific collision responses.

The collider will automatically append itself to the `CollisionManager` Singleton on instantiation.

### Methods
- `sync_with_owner(self, sync_position, sync_rotation, sync_scale)`: 
This method syncronizes the collider's spatial attributes with the owner's. 
By default, it syncs the position and scale, but not the rotation, since `pygame.Rect` does not support rotation.
- `check_collision(self, layers, tags, include_self)`: Used to call the `CollisionManager` 
active instance to check for collisions.

## CollisionManager
The Singleton `CollisionManager` is responsible for managing all colliders in the scene. By mantaining both a list
of colliders and a quadtree to organize them, it serves as a layer interaface for managing all colliders and 
their interactions. The `CollisionManager` uses the **[MonoliteBehaviour](MonoliteBehaviour.md)** system in order
to manage updates.

### Attributes
- `colliders`: A list that contains all colliders currently in the scene.
- `quadtree`: An instance of a quadtree that organizes colliders based on their positions in the world space.
- `_active`: A container for the active instance to properly setup the Singleton pattern, only working when
the instance is active.
- `world_bounds`: A Quadtree.Rectangle boundary that limits world space for quadtree.
- `camera`: A reference for the camera, only used for debugging purposes to visualize the quadtree.

### Methods
- `set_active(cls, instance)`: Changes the active instance of the `CollisionManager` to instance.
- `active(cls)`: Returns the active instance of the `CollisionManager`.
- `draw_debug_boxes(self, surface, camera, color)`: Draws the quadtree boundaries and colliders for 
debugging purposes. It is used automatically on update internally when `ENABLE_COLLISION_DEBUG` flag is
set to `True` in settings.
- `query_collider(cls, collider)`: [UNUSED] Queries the quadtree for potential collisions with 
the provided collider. Returns a list of colliders
-  `get_collisions_active(cls, collider, *, layers, tags, include_self)`: Calls `get_collisions` on the
active instance of `CollisionManager` to check for collisions with the provided collider.
- `get_collisions(self, collider, *, layers, tags, include_self)`: Checks for collisions with the provided
collider by querying the quadtree for potential collisions and then filtering them based on the specified
layers, tags, and whether to include the collider itself in the check. Returns a list of colliders.
- `colliders_any_active(cls, collider, *, layers, tags, include_self)`: Calls `colliders_any` on the
active instance of `CollisionManager` to check for any collisions with the provided collider.
- `colliders_any(self, collider, *, layers, tags, include_self)`: Checks for **ANY** collisions happening 
with the given collider. Returns a boolean.


### How it works
The first instinct when developing a collision system is to just keep a list of all colliders in scene and
check for collisions using the `pygame.Rect` library. By implementing this plainly, we pretty fast incur in
massive framedrops, due to this method's Big O complexity: O(n^2)

This translates to the following:
- If we have 10 colliders, we need to check 100 pairs of colliders for collisions.
- If we have 100 colliders, we need to check 10,000 pairs of colliders for collisions.

And so on. This pretty fast becomes unmanageable, and since the number of colliders in a scene goes up
pretty fast when instantiating enemies, bullets, particles, etc., we need a more efficient way to check 
for collisions.

This is where the concept of **[Quadtrees](./Quadtrees.md)** comes in. By subdividing the space into smaller
quadrants, we can reduce the complexity of collision checks to O(n log n) in the average case, meaning
the performance hugely improves.