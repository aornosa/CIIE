from collections import deque
from core.poolable_object import PoolableObject


class Pool:
    def __init__(self, object_type: type[PoolableObject], starting_size=10):
        self.object_type = object_type
        self.pool = deque([self.object_type() for _ in range(starting_size)])


    def add_new_object(self) -> PoolableObject:
        return self.object_type()

    def _check_available(self, obj: PoolableObject) -> bool:
        return obj in self.pool and obj.is_active() == False

    def _get_available(self) -> PoolableObject:
        if len(self.pool) > 0 and self._check_available(self.pool[0]):
            return self.pool.popleft()
        else:
            return self.add_new_object()

    def acquire(self):
        obj = self._get_available()
        obj.set_active(True)

        # Move to the back of the pool to indicate it's in use
        self.pool.append(obj)
        return obj

    def release(self, obj: PoolableObject):
        if obj in self.pool:
            self.pool.remove(obj)

            # Move to the front of the pool to indicate it's available
            obj.set_active(False)
            self.pool.appendleft(obj)