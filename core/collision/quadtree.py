from __future__ import annotations
import pygame
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.collision.collider import Collider


class Rectangle:
    def __init__(self, x, y, h, w):
        self.x = x
        self.y = y
        self.h = h
        self.w = w

    def bounds(self):
        left = self.x - self.w
        right = self.x + self.w
        top = self.y - self.h
        bottom = self.y + self.h
        return left, right, top, bottom

    def fully_contains(self, item):
        sl, sr, st, sb = self.bounds()
        il, ir, it, ib = item.bounds()

        return (
                il >= sl and
                ir <= sr and
                it >= st and
                ib <= sb)

    def contains(self, item):
        sl, sr, st, sb = self.bounds()
        il, ir, it, ib = item.bounds()

        intersects = not (sr < il or sl > ir or sb < it or st > ib)
        return intersects and not self.fully_contains(item)

    def to_rect(self):
        # Convert to Pygame Rect (x, y, width, height)
        return pygame.Rect(self.x - self.w, self.y - self.h, self.w * 2, self.h * 2)

    @staticmethod
    def from_rect(rect: pygame.Rect):
        x = rect.x + rect.width / 2
        y = rect.y + rect.height / 2
        w = rect.width / 2
        h = rect.height / 2
        return Rectangle(x, y, h, w)


class QuadTree:
    def __init__(self, boundary: Rectangle, capacity):
        self.boundary = boundary
        self.capacity = capacity
        self.items = []

        self.northwest = self.northeast = self.southwest = self.southeast = None
        self.is_divided = False


    def subdivide(self):
        bound = self.boundary

        ne = Rectangle(bound.x + bound.w / 2, bound.y - bound.h / 2, bound.w / 2, bound.h / 2)
        nw = Rectangle(bound.x - bound.w / 2, bound.y - bound.h / 2, bound.w / 2, bound.h / 2)
        se = Rectangle(bound.x + bound.w / 2, bound.y + bound.h / 2, bound.w / 2, bound.h / 2)
        sw = Rectangle(bound.x - bound.w / 2, bound.y + bound.h / 2, bound.w / 2, bound.h / 2)


        self.northeast = QuadTree(ne, self.capacity)
        self.northwest = QuadTree(nw, self.capacity)
        self.southeast = QuadTree(se, self.capacity)
        self.southwest = QuadTree(sw, self.capacity)

        self.is_divided = True


    def insert(self, item: Collider):
        # If item does not intersect this node at all
        if not self.boundary.contains(item.rect) and not self.boundary.fully_contains(item.rect):
            return False

        # Available space + not divided
        if len(self.items) < self.capacity and not self.is_divided:
            self.items.append(item)
            return True

        if not self.is_divided:
            self.subdivide()

        if self.northeast.boundary.fully_contains(item.rect):
            return self.northeast.insert(item)
        if self.northwest.boundary.fully_contains(item.rect):
            return self.northwest.insert(item)
        if self.southeast.boundary.fully_contains(item.rect):
            return self.southeast.insert(item)
        if self.southwest.boundary.fully_contains(item.rect):
            return self.southwest.insert(item)

        # If it overlaps multiple quadrants, keep it here
        self.items.append(item)
        return True

    def clear(self):
        self.items.clear()
        if self.is_divided:
            self.northwest.clear()
            self.northeast.clear()
            self.southwest.clear()
            self.southeast.clear()

    def remove(self, item: Collider):
        if item in self.items:
            self.items.remove(item)
            return True

        if self.is_divided:
            if self.northwest.remove(item):
                return True
            if self.northeast.remove(item):
                return True
            if self.southwest.remove(item):
                return True
            if self.southeast.remove(item):
                return True

        return False

    def query(self, range_rect: Rectangle):
        found = []

        # If range does not intersect this node, return early
        if not self.boundary.contains(range_rect) and not self.boundary.fully_contains(range_rect):
            return found

        # Check items at this node
        for item in self.items:
            if range_rect.contains(item.rect) or range_rect.fully_contains(item.rect) or item.rect.fully_contains(range_rect):
                found.append(item)

        # Check children
        if self.is_divided:
            found.extend(self.northwest.query(range_rect))
            found.extend(self.northeast.query(range_rect))
            found.extend(self.southwest.query(range_rect))
            found.extend(self.southeast.query(range_rect))

        return found