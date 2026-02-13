# Developer Manual: Particles
The `Particle` system is designed to be a lightweight and efficient instantiation solution for 
visual effects that require a large number of short-lived objects, such as explosions, smoke, or fire.

It lives through the implementation of **[Object Pools](./ObjectPools.md)** and 
**[Monolite Behaviours](./MonoliteBehaviour.md)**.

## Particle Emitters
The `ParticleEmitter` class is responsible for managing the emission and rendering of the particles.
It allows for rapid instantiation and management of the particles through an API that leaves the
heavy lifting to the underlying systems, while providing a simple interface for users.

### Methods
- `emit()`: This method is responsible for creating new particles and adding them to the system. It can be called
- `update()`: This method updates the state of all active particles, such as their position, velocity, and lifespan.
*Naturally overrides the `update()` method of the `MonoliteBehaviour` class.*


- `kill_particle(particle)`: By using this method, we can notify the emitter to remove a particle from the active list 
and return it to the pool for future use.

## Particle Class
The `Particle` class is a simple implementation of a poolable object that represents a single particle
in the system. It contains properties such as position, velocity, and lifespan, which can be used to
define the behavior of the particle over time.

### Usage
To use the `Particle` system, you can create an instance of the `ParticleEmitter` class and call the `emit()`
method to start emitting particles. The emitter will handle the creation and lifecycle of the particles, while
the particles themselves will be rendered automatically.

```python
from core.particles.particle_emitter import ParticleEmitter
from core.particles.particle import Particle

# Create a particle
particle_factory = lambda: Particle(asset="assets/particle.png", lifespan=5)

# Create a particle emitter with the factory function
emitter = ParticleEmitter(particle_factory)

emitter.set_position(player.position)
emitter.set_rotation(player.rotation)

# Emit particles
emitter.emit()  # Shoots a particle that will last for 5 seconds
```

### How it works
The `Particle` System works by creating a `particle_factory` of the desired particle, which works as
a template for the emitter to instantiate clones of said particle. By leveraging the Object Pool system, 
the emitter can manage a large volume of visual effects without incurring in a substantial performance drop.
