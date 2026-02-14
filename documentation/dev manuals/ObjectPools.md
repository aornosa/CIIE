# Developer Manual: Object Pools
The `ObjectPool` system is composed of two components: `ObjectPool` and `PoolableObject`. 

The ObjectPools are 
designed to contain multiple instances of the same type of object, in order to optimize performance and avoid
clotting the memory by creating and destroying objects such as particles, bullets, or enemies.

This is especially optimal for objects that are frequently created and destroyed, as it allows for efficient
reuse of existing objects rather than incurring the overhead of instantiating new ones.

## ObjectPool
The `ObjectPool` class is responsible for managing a collection of reusable objects. By using
a double-ended queue (deque), `ObjectPool` allows for quick and efficient object instantiation,
in `O(1)` time complexity.

### Methods
- `add_new_object(obj)`: Adds a new object to the pool, but does not mark it as active. 
Should be used for pre-populating the pool
- `acquire()`: Retrieves an inactive object and marks it as active. 
- `release(obj)`: Returns an object to the pool, marking it as inactive(available) for future use.

#### Internal Methods
- `_get_available()`: Retrieves the first inactive object from the pool. If all objects are active,
a new object is created and returned.
- `_check_available(obj)`: Checks if the provided object is part of the pool and is currently active.

## PoolableObject
The `PoolableObject` class is a base class for objects that can be managed by an `ObjectPool`. It provides a 
simple interface for marking objects as active or inactive, which is essential for the pooling mechanism to 
function correctly.

### Usage
To use an `ObjectPool`, you only need to declare an instance of such, and then call the `acquire()` method
to get an object from the pool, and `release(obj)` to return it when you're done.

```python
from core.pools.object_pool import Pool
from core.pools.poolable_object import PoolableObject


class PoolableExample(PoolableObject):
    def __init__(self):
        super().__init__()


# Optional starting size, default is 10
my_pool = Pool(PoolableExample, starting_size=10)

# Acquire an object from the pool
obj = my_pool.acquire()

# Use the object for some operations
...

# Release the object back to the pool when done
my_pool.release(obj)
```
### How it works
First, the `ObjectPool` sets up a double-ended queue (deque) to store the objects. 
When an object is acquired, the pool checks the first item in the deque. 

If it's inactive, it gets marked as active and returned.

However, if the first item is active, we can safely assume that all other objects in the pool 
are also active, since active objects are moved to the end of the deque. 

In this case, a new object is created, added to the pool, and returned.

When an object is released back to the pool, it gets marked as inactive and moved to the front of the deque,
making it available for future acquisitions.

This has some interesting quirks: 
- The most recently released objects are the first ones to be acquired,
which can be beneficial for performance in certain scenarios, as it may improve cache locality.
- The pool can grow dynamically as needed, but it will never shrink, so it's important to always manage the 
pool size
- Every item is ordered by their last release time, so the most recently released item is always at the front
of the deque, while the least recently released item is at the back.
