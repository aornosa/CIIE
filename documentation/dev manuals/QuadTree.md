# Developer Manual: QuadTree

The `QuadTree` class is a data structure used for spatial partitioning, which allows for efficient
querying of objects based on their positions in a 2D space. It is particularly useful for optimizing
collision detection and other spatial queries in game development. It is used in the `Collision` system

## Rectangle
The `Rectangle` class is a simple data structure that defines a rectangular area in 2D space. It is used
as the basic building block for the `QuadTree` to define the boundaries of each quadrant. The `Rectangle`
class provides methods for checking if a point is contained within the rectangle and if it intersects with
another rectangle.

### Attributes
- `x`: The x-coordinate of the top-left corner of the rectangle.
- `y`: The y-coordinate of the top-left corner of the rectangle.
- `w`: The width of the rectangle.
- `h`: The height of the rectangle.

### Methods
- `bounds(self)`: Returns the boundaries of the rectangle in left, right, top, and bottom format.
- `contains(self, item)`: Checks if a given rectangle is within the bounds of the current rectangle.
- `fully_contains(self, item)`: Checks if a given rectangle is fully contained within the bounds of 
the current rectangle.
- `to_rect(self)`: Converts the rectangle to a format compatible with Pygame's `Rect` class for 
rendering and collision detection.
- `from_rect(rect)`: A class method that creates a `Rectangle` instance from a Pygame `Rect` object.


## QuadTree
The `QuadTree` class is a recursive data structure that divides the 2D space into four quadrants, allowing
for efficient storage and retrieval of objects based on their spatial location. This helps in reducing 
the number of collision checks by only checking collisions in the relevant quadrants.

### Attributes
- `self.boundary`: A `Rectangle` object that defines the area covered by the current node of the quadtree.
- `self.capacity`: The maximum number of items that can be stored in a single node before it needs to be
subdivided into quadrants.
- `self.items`: A list that holds the `Collider` items that are currently stored in the node. 
Each item is expected to have a `rect` attribute that defines its bounding rectangle for collision detection.


- `self.northeast`: Northeastern quadrant child node.
- `self.northwest`: Northwestern quadrant child node.
- `self.southeast`: Southeastern quadrant child node.
- `self.southwest`: Southwestern quadrant child node.


- `self.is_divided`: A boolean flag indicating whether the current node has already been subdivided into
quadrants.

### Methods
- `subdivide(self)`: Divides the rectangle into four equal quadrants 
- `insert(self, item)`: Inserts a `Collider` item into the appropriate quadrant of the quadtree based on its
position.
- `query(self, rect_range)`: Retrieves all `Collider` items that are within a specified rectangular range.
This is used for collision detection to find potential colliders that are near a given object. Use collider.rect
in rect_range to check for the collision with the colliders in the quadtree.
- `clear(self)`: Clears all items from the quadtree, resetting it to an empty state.

### How it works
When an object is inserted into the `QuadTree`, the tree checks if the object's bounding rectangle fits within
the current node's rectangle. If it does, the object is added to the node. If the node exceeds the determined
capacity, it subdivides itself into four quadrants and redistributes the items among the child nodes. 

However, on certain conditions, capacity will be exceeded. For example if the object is larger than the quadrant
size, it will be added to the current node instead of being subdivided further.