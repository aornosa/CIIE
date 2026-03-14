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
        left   = self.x - self.w
        right  = self.x + self.w
        top    = self.y - self.h
        bottom = self.y + self.h
        return left, right, top, bottom

    def fully_contains(self, item):
        sl, sr, st, sb = self.bounds()
        il, ir, it, ib = item.bounds()
        return il >= sl and ir <= sr and it >= st and ib <= sb

    def contains(self, item):
        sl, sr, st, sb = self.bounds()
        il, ir, it, ib = item.bounds()
        # Intersecta pero no contiene completamente
        intersects = not (sr < il or sl > ir or sb < it or st > ib)
        return intersects and not self.fully_contains(item)

    def to_rect(self):
        # Rectangle usa centro + semiancho, Rect usa esquina superior izquierda + tamaño
        return pygame.Rect(self.x - self.w, self.y - self.h, self.w * 2, self.h * 2)

    @staticmethod
    def from_rect(rect: pygame.Rect):
        x = rect.x + rect.width  / 2
        y = rect.y + rect.height / 2
        w = rect.width  / 2
        h = rect.height / 2
        return Rectangle(x, y, h, w)


class QuadTree:
    def __init__(self, boundary: Rectangle, capacity):
        self.boundary  = boundary
        self.capacity  = capacity
        self.items     = []

        self.northwest = self.northeast = self.southwest = self.southeast = None
        self.is_divided = False

    def subdivide(self):
        bound = self.boundary
        hw, hh = bound.w / 2, bound.h / 2

        # Divide en cuatro cuadrantes desplazando el centro en ±hw y ±hh
        self.northeast = QuadTree(Rectangle(bound.x + hw, bound.y - hh, hh, hw), self.capacity)
        self.northwest = QuadTree(Rectangle(bound.x - hw, bound.y - hh, hh, hw), self.capacity)
        self.southeast = QuadTree(Rectangle(bound.x + hw, bound.y + hh, hh, hw), self.capacity)
        self.southwest = QuadTree(Rectangle(bound.x - hw, bound.y + hh, hh, hw), self.capacity)

        self.is_divided = True

    def insert(self, item: Collider):
        if not self.boundary.contains(item.rect) and not self.boundary.fully_contains(item.rect):
            return False

        if len(self.items) < self.capacity and not self.is_divided:
            self.items.append(item)
            return True

        if not self.is_divided:
            self.subdivide()

        # Inserta en el cuadrante que contiene completamente el item
        for child in (self.northeast, self.northwest, self.southeast, self.southwest):
            if child.boundary.fully_contains(item.rect):
                return child.insert(item)

        # Si solapa varios cuadrantes, se queda en este nodo
        self.items.append(item)
        return True

    def clear(self):
        self.items.clear()
        if self.is_divided:
            for child in (self.northwest, self.northeast, self.southwest, self.southeast):
                child.clear()

    def remove(self, item: Collider):
        if item in self.items:
            self.items.remove(item)
            return True

        if self.is_divided:
            for child in (self.northwest, self.northeast, self.southwest, self.southeast):
                if child.remove(item):
                    return True

        return False

    def query(self, range_rect: Rectangle):
        if not self.boundary.contains(range_rect) and not self.boundary.fully_contains(range_rect):
            return []

        found = [
            item for item in self.items
            if range_rect.contains(item.rect)
            or range_rect.fully_contains(item.rect)
            or item.rect.fully_contains(range_rect)
        ]

        if self.is_divided:
            for child in (self.northwest, self.northeast, self.southwest, self.southeast):
                found.extend(child.query(range_rect))

        return found