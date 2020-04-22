import pygame
import time
from pygame import draw
from random import randint


class Display_window():

    def __init__(self):
        # These get changed to true once they have been used
        # The start and finish_tile_pos tiles can only be placed once
        self.start_tile = False
        self.finish_tile = False
        self.wall_tile = True
        # When configuring dimension sizes
        # box_dimension should be a factor of border_length
        self.border_length = 900
        self.box_dimension = 30
        self.window_dimension = (self.border_length, self.border_length)
        # Debug used to visualize squares as path finding performs
        # will be considerably slower to solve however
        self.debug = False
        self.debug_time = 1/2
        self.gameDisplay = pygame.display.set_mode(self.window_dimension)
        pygame.display.set_caption("Path Finding")
        self.clock = pygame.time.Clock()
        # Need to be declared before hand to prevent if statements throwing errors
        self.crashed = False
        self.solved = False
        self.ready = False
        self.complete = False
        self.unsolvable = False
        # The colors used for drawing so they're not assigned each time
        # there is a new frame and colors are drawn
        self.Colors = {
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "grey": (128, 128, 128),
            "cyan": (0, 255, 255),
            "orange": (255, 128, 0),
            "pink": (230, 0, 115),
            "yellow": (255, 221, 51)
        }
        self.create_grid()
        self.update()

    def create_grid(self):
        # Empty grid with all values set to None that can later be changed
        self.grid = [[None for y in range(self.border_length // self.box_dimension)] for x in range(self.border_length // self.box_dimension)]

    def draw_grid(self):
        # Draws each tile depending on their colour associated on the grid
        # The position of each tile increments by the width of the tiles each time
        posY = 0
        for row in range(len(self.grid)):
            posX = 0
            for col in range(len(self.grid[0])):
                if self.grid[row][col] is None:
                    pygame.draw.rect(self.gameDisplay, self.Colors["white"], (posX, posY, self.box_dimension, self.box_dimension), 1)
                if self.grid[row][col] == 1:
                    pygame.draw.rect(self.gameDisplay, self.Colors["green"], (posX, posY, self.box_dimension, self.box_dimension), 0)
                if self.grid[row][col] == 2:
                    pygame.draw.rect(self.gameDisplay, self.Colors["red"], (posX, posY, self.box_dimension, self.box_dimension), 0)
                if self.grid[row][col] == 3:
                    pygame.draw.rect(self.gameDisplay, self.Colors["grey"], (posX, posY, self.box_dimension, self.box_dimension), 0)
                if self.grid[row][col] == 4:
                    pygame.draw.rect(self.gameDisplay, self.Colors["cyan"], ((posX + (self.box_dimension // 4)), (posY + (self.box_dimension // 4)), (self.box_dimension // 2), (self.box_dimension) // 2), 0)
                if self.grid[row][col] == 5 and self.debug:
                    pygame.draw.rect(self.gameDisplay, self.Colors["yellow"], ((posX + (self.box_dimension // 4)), (posY + (self.box_dimension // 4)), (self.box_dimension // 2), (self.box_dimension) // 2), 0)
                if self.grid[row][col] == 6 and self.debug:
                    pygame.draw.rect(self.gameDisplay, self.Colors["pink"], ((posX + (self.box_dimension // 4)), (posY + (self.box_dimension // 4)), (self.box_dimension // 2), (self.box_dimension) // 2), 0)
                posX += self.box_dimension
            posY += self.box_dimension

    def update_grid(self):
        # This code only needs to be run before the solver starts
        if not self.ready:
            # Gets the mouse coordiante position
            grid = pygame.mouse.get_pos()
            x = grid[0] // self.box_dimension
            y = grid[1] // self.box_dimension
            # Sets the position for the start tile if not already available
            if not self.start_tile:
                self.start_tile_pos = (y, x)
                self.grid[y][x] = 1
                self.start_tile = True
                self.finish_tile = False
            # Sets the position for the finish tile if not already available
            elif not self.finish_tile:
                self.finish_tile_pos = (y, x)
                if self.finish_tile_pos != self.start_tile_pos:
                    self.grid[y][x] = 2
                    self.finish_tile = True
                    self.wall_tile = False
            # Any clicks after are created as wall tiles
            elif not self.wall_tile and not self.ready and ((y, x) != self.start_tile_pos and (y, x) != self.finish_tile_pos):
                self.grid[y][x] = 3

    def calculate_distance(self, pos1, pos2):
        # Supply to cordinates and uses pythagoras to work out the distance
        distance = ((pos2[1] - pos1[1])**2 + (pos2[0] - pos1[0])**2)**0.5
        return distance

    def calculate_f_cost(self, pos):
        # Distance between node and start
        g_cost = self.calculate_distance(pos, self.start_tile_pos)
        # Distance between node and finish_tile_pos
        h_cost = self.calculate_distance(pos, self.finish_tile_pos)
        # G and H combined
        f_cost = g_cost + h_cost
        return f_cost

    def check_neighbour(self, position):
        # The index of surrounding tiles from the given positions
        top_left = (position[0] - 1, position[1] - 1)
        top_right = (position[0] - 1, position[1] + 1)
        bottom_left = (position[0] + 1, position[1] - 1)
        bottom_right = (position[0] + 1, position[1] + 1)
        top = (position[0] - 1, position[1])
        bottom = (position[0] + 1, position[1])
        left = (position[0], position[1] - 1)
        right = (position[0], position[1] + 1)
        # Stores all the positions in an array
        neighbours = [top_left, top_right, bottom_left, bottom_right, top, bottom, left, right]
        return self.valid_neighbour(neighbours)

    def valid_neighbour(self, neighbour):
        # Removes surrounding Tiles that are less than 0 or greater than
        # the max tiles in x / y direction
        to_remove = []
        for index in neighbour:
            y, x = index
            if (y < 0) or (x < 0) or (y >= (self.border_length / self.box_dimension)) or (x >= (self.border_length / self.box_dimension)) or (self.grid[y][x] == 3):
                to_remove.append(index)
        # Doesn't remove beforehand otherwise it misses out invalid positions
        for index in to_remove:
            neighbour.remove(index)
        return(neighbour)

    def update(self):
        # Events to happen while game is passively running
        while not self.crashed:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.crashed = True
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.update_grid()
                if event.type == pygame.KEYDOWN:
                    # User can only attemp to solve once there is a start and finish tile on screen
                    if event.key == ord(" ") and self.start_tile and self.finish_tile:
                        self.solve_problem()
                    elif event.key == ord("r"):
                        self.reset_board()
                    elif event.key == ord("g"):
                        self.generate_board()
                        self.draw_grid()
                        pygame.display.update()
                        time.sleep(1)
                        self.solve_problem()
            self.draw_grid()
            pygame.display.update()
            self.clock.tick(60)
        pygame.quit()
        quit()

    def solve_problem(self):
        self.ready = True
        self.f_cost_pos()
        # Sets the current position to be the start position as that's where to start searching from
        self.current_position = [self.start_tile_pos, self.calculate_f_cost(self.start_tile_pos), True, self.start_tile_pos]
        self.f_grid[self.start_tile_pos[0]][self.start_tile_pos[1]] = self.current_position
        self.check_neighbour_loop()
        # While the problem can continue to be solvable, keep trying to find a solution
        if not self.unsolvable:
            self.produce_solved_solution()
            self.finish_grid()

    def f_cost_pos(self):
        # A grid for storing index, f costs, open / closed and last index
        self.f_grid = [[None for y in range(self.border_length // self.box_dimension)] for x in range(self.border_length // self.box_dimension)]

    def find_lowest_f_cost(self):
        lowest_found = None
        for y in range(len(self.f_grid)):
            for x in range(len(self.f_grid)):
                if self.f_grid[y][x] is not None:
                    if self.f_grid[y][x][2]:
                        # If None there's no information about the available node yet
                        if lowest_found is None:
                            lowest_found = self.f_grid[y][x]
                        # Finds the lowest value and overwrites if lower than the one stored
                        elif self.f_grid[y][x][1] < lowest_found[1]:
                            lowest_found = self.f_grid[y][x]
        return lowest_found

    def check_neighbour_loop(self):
        while True:
            # Checks if the solution has been found
            if self.current_position[0] == self.finish_tile_pos:
                self.solved = True
                break
            # Sets a list with all the available surrounding nodes
            available_neighbours = self.check_neighbour(self.current_position[0])
            neighbours_with_cost = []
            # A format for storing each node in the array
            for index in available_neighbours:
                neighbours_with_cost.append([index, self.calculate_f_cost(index), True, self.current_position[0]])
                if self.debug and self.grid[index[0]][index[1]] != 1 and self.grid[index[0]][index[1]] != 2 and self.grid[index[0]][index[1]] != 6:
                    self.grid[index[0]][index[1]] = 5
            for index in neighbours_with_cost:
                if self.f_grid[index[0][0]][index[0][1]] is None:
                    self.f_grid[index[0][0]][index[0][1]] = index
                # Updates the f_grid only if lower than the one previously there
                elif self.f_grid[index[0][0]][index[0][1]][1] < index[1]:
                    self.f_grid[index[0][0]][index[0][1]] = index
            self.f_grid[self.current_position[0][0]][self.current_position[0][1]][2] = False
            if self.debug:
                last = self.current_position
            # Finds the lowest f cost tile on screen for next current pos
            self.current_position = self.find_lowest_f_cost()
            if not self.check_open():
                self.unsolvable = True
                print("Cannot be solved")
                break
            if self.debug:
                # Changes the last position / current position to a different colour to indicate what has been searched / known
                if self.grid[last[0][0]][last[0][1]] != 1 and self.grid[last[0][0]][last[0][1]] != 2 and self.grid[last[0][0]][last[0][1]] != 6:
                    self.grid[last[0][0]][last[0][1]] = 5
                if self.grid[self.current_position[0][0]][self.current_position[0][1]] != 1 and self.grid[self.current_position[0][0]][self.current_position[0][1]] != 2:
                    self.grid[self.current_position[0][0]][self.current_position[0][1]] = 6
                # Draws the grid again to reflect the changes that have been made
                self.draw_grid()
                pygame.display.update()
                time.sleep(self.debug_time)

    def produce_solved_solution(self):
        # An array to store the solution in
        self.tile_order = []
        self.tile_order.append(self.finish_tile_pos)
        first_step = (self.f_grid[self.finish_tile_pos[0]][self.finish_tile_pos[1]][3])
        self.tile_order.append(first_step)
        # Back tracks from the last position of each node on the finish to trace back the shortest path to the start
        while True:
            first_step = self.f_grid[first_step[0]][first_step[1]][3]
            self.tile_order.append(first_step)
            # Once it reaches back to the start, otherwise it would
            # keep looping
            if self.f_grid[first_step[0]][first_step[1]][3] == self.f_grid[first_step[0]][first_step[1]][0]:
                break

    def finish_grid(self):
        # Uses the array of index's for the solution and changes them to have the solution colour
        for index in self.tile_order:
            self.grid[index[0]][index[1]] = 4

    def check_open(self):
        # Finds if any of the available slots that have been discovered
        # those not None are open or closed
        # if none of them are open (True) then there are no solutions
        slot_open = False
        for index in self.f_grid:
            for y in index:
                if y is not None:
                    if y[2]:
                        slot_open = True
                        break
        return slot_open

    def reset_board(self):
        self.f_cost_pos()
        self.create_grid()
        self.start_tile = False
        self.finish_tile = False
        self.wall_tile = True
        # When configuring dimension sizes
        # box_dimension should be a factor of border_length
        # Debug used to visualize squares as path finding performs
        # will be considerably slower to solve however
        # Need to be declared before hand to prevent if statements throwing errors
        self.crashed = False
        self.solved = False
        self.ready = False
        self.complete = False
        self.unsolvable = False
        pygame.draw.rect(self.gameDisplay, self.Colors["black"], (0, 0, self.border_length, self.border_length), 0)
    
    def generate_board(self):
        self.reset_board()
        self.random_start()
        self.random_finish()

    def generate_position(self):
        y = randint(0, (self.border_length // self.box_dimension) - 1)
        x = randint(0, (self.border_length // self.box_dimension) - 1)
        return (y, x)

    def random_start(self):
        y, x = self.generate_position()
        self.start_tile_pos = (y, x)
        self.grid[y][x] = 1
        self.start_tile = True
        self.finish_tile = False

    def random_finish(self):
        while True:
            y, x = self.generate_position()
            self.finish_tile_pos = (y, x)
            if self.finish_tile_pos != self.start_tile_pos:
                self.grid[y][x] = 2
                self.finish_tile = True
                self.wall_tile = False
                break

Display_window()
