# Developer Manual: Objects
In this engine, an `Object` is defined as the core entity that represents any element with a position,
rotation, scale that needs to be rendered independently. 

## Object Class 
The `Object` class is conformed by a set of base attributes (position, rotation, scale), that manage
the transformations of a certain asset in the game world. With the aid of a few external and internal
functions, any `Object` can be safely and efficiently rendered, managed and updated in the game loop.

### Methods
- `set_position(position)`: Sets the position (2-tuple) of the object in the game world.
- `set_rotation(angle)`: Sets the rotation of the object in degrees.
- `set_scale(scale)`: Sets the scale (2-tuple) of the object in the game world


- `get_position()`: Returns the current position of the object as a tuple (x, y).
- `get_rotation()`: Returns the current rotation of the object in degrees.
- `get_scale()`: Returns the current scale of the object as a tuple (x, y).


- `draw(surface, camera)`: Renders the object onto the provided surface. This method can be overridden 
if needed for another specific rendering behavior. The `camera` parameter is used to adjust the object's 
position based on the camera's view.

#### Internal Methods
- `_get_scaled_asset()`: Efficiently gets a scaled version of the object's asset. 
This method is used internally to avoid redundant scaling operations, saving performance
- `_rebuild_cache()`: Rebuilds the internal cache of the object, which is used to optimize rendering.

### Usage
In order to use an `Object`, you typically create a subclass that inherits from `Object` and uses its
methods to manage the object's transformations and rendering. For example:

```python
from core.object import Object
class MyObject(Object):
    def __init__(self, asset):
        super().__init__(asset)
        self.asset = asset  # This should be a Pygame surface or similar
    
    # Your functions here...


...
# Create an instance of MyObject
loaded_asset = ...  # Load your asset here (e.g., using pygame.image.load)
my_object = MyObject(loaded_asset) # Accepts position, rotation and scale overloads
my_object.set_position((0,0))
my_object.set_rotation(10)

my_object.draw()
```

However, you can also use an instance the class `Object` by itself, like:
```python
from core.object import Object

asset = ...
my_object = Object(asset)
```

### How it works
On its surface, the `Object` class works as a base for every rendered object. However, internally,
this class works using a cache of the most recent states in order to massively optimize and boost 
performance.