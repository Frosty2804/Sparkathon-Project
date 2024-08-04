import pygame, sys

from pygame.rect import Rect
from map import map_grid
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement
import os
import json
import settings

item_pos = []

class Pathfinder:
	def __init__(self, map_grid):

		# setup
		self.map_grid = map_grid
		self.grid = Grid(matrix = map_grid)
		self.select_tile_icon = pygame.image.load('assets/map/selection.png').convert_alpha()

		# pathfinding
		self.path = []

		# Blip
		self.blip = pygame.sprite.GroupSingle(Blip(self.empty_path))

	def read_file():
		if os.path.exists("shared.json"):
			with open("shared.json", "r") as file:
				global item_pos
				item_pos = json.load(file)
		return []

	def empty_path(self):
		self.path = []

	def draw_active_cell(self):
		mouse_pos = pygame.mouse.get_pos()
		row =  mouse_pos[1] // tile_size
		col =  mouse_pos[0] // tile_size
		current_cell_value = self.map_grid[row][col]
		if current_cell_value == 1:
			rect = pygame.Rect((col * tile_size, row * tile_size), (tile_size, tile_size))
			screen.blit(self.select_tile_icon, rect)

	def create_path(self):
		# start
		start_x, start_y = self.blip.sprite.get_coord()
		start = self.grid.node(start_x,start_y)

		# end
		mouse_pos = pygame.mouse.get_pos()

		#end_x,end_y =  mouse_pos[0] // tile_size, mouse_pos[1] // tile_size
		print(settings.position)
		end_x,end_y = settings.position[0], settings.position[1]
		end = self.grid.node(end_x,end_y)

		# create path
		finder = AStarFinder(diagonal_movement = DiagonalMovement.always)
		self.path, _ = finder.find_path(start, end, self.grid)
		self.grid.cleanup()
		self.blip.sprite.set_path(self.path)

	def draw_path(self):   # draws a visual representation of the path
		if self.path:
			points = []
			for point in self.path:
				x = (point.x * tile_size) + tile_size / 2
				y = (point.y * tile_size) + tile_size / 2
				points.append((x,y))
				pygame.draw.circle(screen, '#4a4a4a', (x,y), 2)

			pygame.draw.lines(screen, '#4a4a4a', False, points, 5)

	def update(self):
		self.draw_active_cell()
		self.draw_path()

		# blip updating and drawing
		self.blip.update()
		self.blip.draw(screen)

class Blip(pygame.sprite.Sprite):
	def __init__(self, empty_path):

		# basic
		super().__init__()
		self.image = pygame.image.load('assets/map/blip.png').convert_alpha()
		# self.rect = self.image.get_rect(center = (60,60))
		self.rect = Rect(60,60, tile_size, tile_size)

		# movement
		self.pos = self.rect.center
		self.speed = 3
		self.direction = pygame.math.Vector2(0,0)

		# path
		self.path = []
		self.collision_rects = []
		self.empty_path = empty_path

	def get_coord(self):
		col = self.rect.centerx // tile_size
		row = self.rect.centery // tile_size
		return (col,row)

	def set_path(self, path):
		self.path = path
		self.create_collision_rects()
		self.get_direction()  # get the direction of the next point after collision

	def create_collision_rects(self):  # create collision rects for each point in the path, to check for collision
		if self.path:
			self.collision_rects = []
			for point in self.path:
				x = (point.x * tile_size) + tile_size / 2
				y = (point.y * tile_size) + tile_size / 2
				rect = pygame.Rect((x - blip_width / 2 , y - blip_height / 2),(8,8))
				self.collision_rects.append(rect)

	def get_direction(self):
		if self.collision_rects:
			start = pygame.math.Vector2(self.pos)
			end = pygame.math.Vector2(self.collision_rects[0].center)
			self.direction = (end - start).normalize()
		else:
			self.direction = pygame.math.Vector2(0,0)
			self.path = []

	def check_collisions(self):
		if self.collision_rects:
			for rect in self.collision_rects:
				if rect.collidepoint(self.pos):
					del self.collision_rects[0]
					self.get_direction()
		else:
			self.empty_path()

	def update(self):
		self.pos += self.direction * self.speed
		self.check_collisions()
		self.rect.center = self.pos   # workaround to not lose data when converting to int

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1312,832))
clock = pygame.time.Clock()

# game setup
bg_surf = pygame.image.load('assets/map/map.png').convert()
tile_size = 32
blip_width, blip_height = 4, 4
pathfinder = Pathfinder(map_grid)

while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()
		if event.type == pygame.MOUSEBUTTONDOWN:  # create path only on mouse click
			pathfinder.create_path()

	screen.blit(bg_surf,(0,0))
	pathfinder.update()

	pygame.display.update()
	clock.tick(60)
