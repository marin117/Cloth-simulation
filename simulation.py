import pygame
from pygame import Vector2 as Vector2D
import math
import time
import sys
from abc import ABC, abstractmethod

GRAVITY = Vector2D(0, 9.81)
WHITE = (255, 255, 255)
RAD = 5
REST_LENGTH = 50


class Point:
    def __init__(self, pos):
        self.pos = pos
        self.old_pos = Vector2D(pos.x - REST_LENGTH, pos.y - REST_LENGTH)
        self.a = Vector2D(0.0, 0.0)
        self.t = 16.
        self.mass = 0.0004

    def add_force(self, force):
        if self.mass != 0.0:
            self.a = force

    def accumulate_forces(self):
        self.a += self.mass * GRAVITY

    def vervlet_integration(self):
        prev_pos = self.pos
        self.pos += self.pos - self.old_pos + self.a * self.t**2
        self.old_pos = prev_pos

    def update(self):
        self.accumulate_forces()
        self.vervlet_integration()


class Spring:
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __str__(self):
        return f'start: {self.start} end: {self.end}'


class Cloth:
    def __init__(self, density, draw_strategy) -> None:
        self.num_rows, self.num_cols = density
        self.particles = []
        self.springs = []
        self.strategy = draw_strategy

        for row in range(1, self.num_rows + 1):
            for col in range(1, self.num_cols + 1):
                pos = Vector2D(float(col * REST_LENGTH) - 50, float(row * REST_LENGTH) - 50)
                self.particles.append(Point(pos))

        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if(j < self.num_cols - 1):
                    self.springs.append(Spring((j * self.num_rows) + i, ((j+1) * self.num_rows) + i))
                if(i < self.num_rows - 1):
                    self.springs.append(Spring((j * self.num_rows) + i, (j * self.num_rows) + i+1))
                if j < self.num_cols - 1 and i < self.num_rows - 1:
                    self.springs.append(Spring((j * self.num_rows) + i, ((j+1) * self.num_rows) + i + 1))
                    self.springs.append(Spring((j * self.num_rows) + i + 1, ((j+1) * self.num_rows) + i))

        self.particles[0].mass = 0
        self.particles[self.num_rows-1].mass = 0

    def update(self, start_time):
        for(index, spring) in enumerate(self.springs):
            delta = self.particles[spring.end].pos - self.particles[spring.start].pos
            delta_length = math.sqrt(delta * delta)
            diff = (delta_length - REST_LENGTH) / (delta_length * (self.particles[spring.end].mass + self.particles[spring.start].mass)) 
            self.particles[spring.start].pos += self.particles[spring.start].mass * delta * diff * 0.5
            self.particles[spring.end].pos -= self.particles[spring.end].mass * delta * diff * 0.5

        for index, point in enumerate(self.particles):
            self.particles[index].t = clock.get_time()
            self.particles[index].add_force(Vector2D(0.002 * math.sin(time.time() - start_time), 0.002 * math.sin(time.time() - start_time)))
            self.particles[index].update()

    def draw(self):
        for i in range(self.num_rows):
            for j in range(self.num_cols):
                if(j < self.num_cols - 1):
                    start = (j * self.num_rows) + i
                    end = ((j+1) * self.num_rows) + i
                    self.strategy.draw(self.particles[start].pos, self.particles[end].pos)
                    self.springs.append(Spring((j * self.num_rows) + i, ((j+1) * self.num_rows) + i))
                if(i < self.num_rows - 1):
                    start = (j * self.num_rows) + i
                    end = (j * self.num_rows) + i+1
                    self.strategy.draw(self.particles[start].pos, self.particles[end].pos)


class DrawStrategy:
    @abstractmethod
    def draw(self, start, end):
        pass


class PyGameDrawStrategy(DrawStrategy):
    def draw(self, start, end):
        pygame.draw.line(screen, WHITE, start, end)


pygame.init()

size = width, height = 800, 600
screen = pygame.display.set_mode(size)

clock = pygame.time.Clock()

cloth = Cloth([6, 6], PyGameDrawStrategy())


start_time = time.time()

while True:
    screen.fill((0, 0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT: sys.exit()

    cloth.update(start_time)
    cloth.draw()

    pygame.display.update()
    clock.tick(30)

