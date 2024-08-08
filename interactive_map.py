import pygame, sys
import target_position
from pygame.rect import Rect
from map import map_grid
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from pathfinding.core.diagonal_movement import DiagonalMovement															#CHECK LATER
from time import sleep
import dash
from dash.dependencies import Output, Input
from dash import dcc, html, dcc
from datetime import datetime
import json
import plotly.graph_objs as go
from collections import deque
from flask import Flask, request
import threading


pygame.mixer.init()		#FOR AUDIO
# pygame.time.wait(10000)	#YOU CAN DELETE

side = 0
old_side = 0

global tile_size, blip_height, blip_width
global balls #My balls
x = 0
y = 0
z = 0

server = Flask(__name__)
app = dash.Dash(__name__, server=server)

MAX_DATA_POINTS = 1000
UPDATE_FREQ_MS = 100

time = deque(maxlen=MAX_DATA_POINTS)
accel_x = deque(maxlen=MAX_DATA_POINTS)
accel_y = deque(maxlen=MAX_DATA_POINTS)
accel_z = deque(maxlen=MAX_DATA_POINTS)

app.layout = html.Div(
	[
		dcc.Markdown(
			children="""
			# Live Sensor Readings
			Streamed from Sensor Logger: tszheichoi.com/sensorlogger
		"""
		),
		dcc.Graph(id="live_graph"),
		dcc.Interval(id="counter", interval=UPDATE_FREQ_MS),
	]
)


@app.callback(Output("live_graph", "figure"), Input("counter", "n_intervals"))
def update_graph(_counter):
	data = [
		go.Scatter(x=list(time), y=list(d), name=name)
		for d, name in zip([accel_x, accel_y, accel_z], ["X", "Y", "Z"])
	]

	graph = {
		"data": data,
		"layout": go.Layout(
			{
				"xaxis": {"type": "date"},
				"yaxis": {"title": "Acceleration ms<sup>-2</sup>"},
			}
		),
	}
	if (
		len(time) > 0
	):  #  cannot adjust plot ranges until there is at least one data point
		graph["layout"]["xaxis"]["range"] = [min(time), max(time)]
		graph["layout"]["yaxis"]["range"] = [
			min(accel_x + accel_y + accel_z),
			max(accel_x + accel_y + accel_z),
		]

	return graph


@server.route("/data", methods=["POST"])
def data():  # listens to the data streamed from the sensor logger
	if str(request.method) == "POST":
		# print(f'received data: {request.data}')
		data = json.loads(request.data)
		for d in data['payload']:
			if (
				d.get("name", None) == "magnetometer" #"accelerometer"
			):  #  modify to access different sensors
				ts = datetime.fromtimestamp(d["time"] / 1000000000)
				if len(time) == 0 or ts > time[-1]:
					time.append(ts)
					# modify the following based on which sensor is accessed, log the raw json for guidance
					global x, y, z
					x_value = int(d["values"]["x"])
					y_value = int(d["values"]["y"])
					z_value = int(d["values"]["z"])
					x = x_value
					y = y_value
					z = z_value
					# sleep(1)

					print(f'X, Y, Z : {x_value} {y_value} {z_value}')
					accel_x.append(d["values"]["x"])
					accel_y.append(d["values"]["y"])
					accel_z.append(d["values"]["z"])
	return "success"


def run_dash():
    app.run_server(port=8000, host="0.0.0.0")


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

	def empty_path(self):
		self.path = []

	def draw_target(self):
		row =  target_position.position[1] // tile_size
		col =  target_position.position[0] // tile_size
		current_cell_value = self.map_grid[row][col]
		if current_cell_value == 1:
			rect = pygame.Rect((col * tile_size, row * tile_size), (tile_size, tile_size))
			screen.blit(self.select_tile_icon, rect)

	def create_path(self):
		# start
		start_x, start_y = self.blip.sprite.get_coord()
		start = self.grid.node(start_x,start_y)

		# end
		end_x,end_y = target_position.position[0] // tile_size, target_position.position[1] // tile_size
		end = self.grid.node(end_x,end_y)

		# create path
		finder = AStarFinder(diagonal_movement = DiagonalMovement.always)
		# '_' stores the no of runs, not necessary for this demo
		self.path, _ = finder.find_path(start, end, self.grid)
		self.grid.cleanup()
		self.blip.sprite.set_path(self.path)

	def draw_path(self):   # draws a visual representation of the path
		if self.path:
			points = []
			global balls
			balls = points
			for point in self.path:
				#print(points)

				x = (point.x * tile_size) + tile_size / 2
				y = (point.y * tile_size) + tile_size / 2
				points.append((x,y))
				pygame.draw.circle(screen, '#4a4a4a', (x,y), 10)

		if len(points) > 1:
			pygame.draw.lines(screen, '#4a4a4a', False, points, 5)

	def update(self):
		self.draw_target()
		self.draw_path()

		# blip updating and drawing
		self.blip.update()
		self.blip.draw(screen)

class Blip(pygame.sprite.Sprite):
	def __init__(self, empty_path):

		# basic
		super().__init__()
		self.image = pygame.image.load('assets/map/blip.png').convert_alpha()
		self.rect = Rect(100,100, .01, .01)
		#self.rect = Rect(60,60, tile_size, tile_size)

		# movement
		self.pos = self.rect.center

		self.speed =  pygame.math.Vector2(3,3)#[3,3]
		self.speed.x = 3
		self.speed.y = 3

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

	# def get_direction(self):
	# 	if self.collision_rects:
	# 		start = pygame.math.Vector2(self.pos)
	# 		end = pygame.math.Vector2(self.collision_rects[0].center)
	# 		if len(self.direction) != 0:
	# 			self.direction = (end - start).normalize()
	# 		# print(self.direction)
	# 	else:
	# 	    # if destination reached, quit the game
	# 		self.direction = pygame.math.Vector2(0,0)
	# 		self.path = []
	# 		pygame.quit()
	# 		sys.exit()

	def get_direction(self):
		if not self.collision_rects or pygame.Vector2(self.rect.center).distance_to(pygame.Vector2(target_position.position[0], target_position.position[1])) < 65:
            # if destination reached, quit the game
			self.direction = pygame.math.Vector2(0, 0)
			self.path = []
			pygame.quit()
			sys.exit()
		else:
			start = pygame.math.Vector2(self.pos)
			end = pygame.math.Vector2(self.collision_rects[0].center)
			if len(self.direction) != 0:
				self.direction = (end - start).normalize()

	def check_collisions(self):
		if self.collision_rects:
			for rect in self.collision_rects:
				if rect.collidepoint(self.pos):
					del self.collision_rects[0]
					self.get_direction()
		else:
			self.empty_path()

	def update(self):
		global balls, old_side, side
		#Displacement between first two elements of points tuple(which contains all the circles leading to path)
		if len(balls) > 1:
			x1 = balls[0][0]
			x2 = balls[1][0]
			y1 = balls[0][1]
			y2 = balls[1][1]
			xdisplace = x2 - x1
			ydisplace = y2 - y1
			displacement = [xdisplace, ydisplace]



			#For the next block of code
			if displacement[1] > 0: #DOWN
				side = 3
			elif displacement[1] < 0: #UP
				side = 4
			elif displacement[0] > 0: #RIGHT
				side = 1
			elif displacement[0] < 0: #LEFT
				side = 2
			else:
				pass

			#IF DIRECTION OF PATH STILL HASNT CHANGED WRT TO PLAYER THEN DONT PLAY ANY AUDIO
			if old_side != side:
				old_side = side
				if side == 1:
					pygame.mixer.music.load("audio/MoveRight.mp3")
				elif side == 2:
					pygame.mixer.music.load("audio/MoveLeft.mp3")
				elif side == 3:
					pygame.mixer.music.load("audio/HeadDown.mp3")
				elif side == 4:
					pygame.mixer.music.load("audio/HeadUp.mp3")
				else:
					pass
				if not(pygame.mixer.music.get_busy()):
					pygame.mixer.music.play()


		#KEYS
		keys = pygame.key.get_pressed()
		if keys[pygame.K_UP]:
			self.speed.y = -3
		elif keys[pygame.K_DOWN]:
			self.speed.y = +3
		else:
			self.speed.y = 0

		if keys[pygame.K_LEFT]:
			self.speed.x = -3
		elif keys[pygame.K_RIGHT]:
			self.speed.x = +3
		else:
			self.speed.x = 0

		#NORMALIZED
		if self.speed.magnitude() != 0:
			self.pos += pygame.math.Vector2(self.speed.x , self.speed.y).normalize() * 3


		self.check_collisions()
		self.rect.center = self.pos   # workaround to not lose data when converting to int

# pygame setup
def run_pygame():
	pygame.init()
	global screen
	screen = pygame.display.set_mode((1312,832))
	clock = pygame.time.Clock()

	global tile_size, blip_height, blip_width
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
			else:
				pathfinder.create_path()

		screen.blit(bg_surf,(0,0))
		pathfinder.update()

		pygame.display.update()
		clock.tick(60)

if __name__ == "__main__":
	dash_thread = threading.Thread(target=run_dash)			#run_dash() and run_pygame() run simultaneosly by threading module
	dash_thread.start()
	run_pygame()
