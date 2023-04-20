import pygame
import sys
import pygame_gui
import time
from Element import Element
from Cell import Cell

WIDTH = 1400
HEIGHT = 800
ROWS = 100
COLS = 100
CELL_SIZE = WIDTH // COLS

VOID = (0, 0, 0)
SAND = (255, 255, 0)
ROCK = (128, 128, 128)
GRASS = (0, 255, 0)
WATER = (0, 0, 255)
LAVA = (255, 0, 0)
VAPOR = (0, 255, 255)
HELIUM = (0, 255, 128)
ICE = (0, 180, 180)

void = Element(VOID, 0, 0, "Void", 0)
sand = Element(SAND, 1, 1, "Sand", 0)
rock = Element(ROCK, 0, 2, "Rock", 0)
grass = Element(GRASS, 0, 3, "Grass",0)
water = Element(WATER, 1, 4, "Water",23)
lava = Element(LAVA, 1, 5, "Lava",1000)
vapor = Element(VAPOR, -1, 6, "Vapor",200)
helium = Element(HELIUM, 1, 7, "Helium",-100)
ice = Element(ICE, 0, 8, "Ice",0)

listElement = [void, sand, rock, grass, water, lava, vapor, helium, ice]

# Set up clock
clock = pygame.time.Clock()
FPS = 60  # Frames per second

# Initialize pygame
pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulation")

# Create a pygame_gui.UIManager
ui_manager = pygame_gui.UIManager((WIDTH, HEIGHT))

reset_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((350, 300), (100, 40)),
                                            text='Reset',
                                            manager=ui_manager
                                            )
dropdown_menu = pygame_gui.elements.UIDropDownMenu(
    # get All name of item where are int the elementList
    options_list=[element.name for element in listElement],
    starting_option='Sand',
    relative_rect=pygame.Rect((350, 200), (100, 30)),
    manager=ui_manager)

# Create a 2D list and create Cell object at each
grid = [[Cell() for col in range(COLS)] for row in range(ROWS)]

# Keep track of mouse button status
mouse_down = False

def updateElements():
    # Balayage bas vers haut
    for row in reversed(range(ROWS - 1)):
        for col in range(COLS):
            # Floor
            if grid[row][col].element.gravity == 1:
                if grid[row + 1][col].element.id == 0:
                    updatePositionElements(row, col, 1)
                    if grid[row][col].element.id == 4:
                        radiusTemp(row, col, 1)
                    if grid[row][col].element.id == 7:
                        radiusTemp(row, col, 1)
                    if grid[row][col].element.id == 5:
                        radiusTemp(row, col, 1)

            # Transformation
            if grid[row][col].temperature > 100:
                if grid[row][col].element.id == 4:
                    placeElement(row, col, vapor)
                if grid[row][col].element.id == 7:
                    placeElement(row, col, water)
            if grid[row][col].temperature <= -100:
                if grid[row][col].element.id == 4:
                    placeElement(row, col, ice)
                if grid[row][col].element.id == 6:
                    placeElement(row, col, water)

    # Balayage haut vers bas
    for row in range(ROWS - 1):
        for col in range(COLS):
            if grid[row][col].element.gravity == -1:
                if grid[row - 1][col].element.gravity == 1 or grid[row - 1][col].element.id == 0:
                    permutationElement(row, col, grid[row][col].element.gravity)
    time.sleep(1 / FPS)


def permutationElement(row, col, gravity):
    element_id_to_replace = grid[row + gravity][col].element
    element_id_target = grid[row][col].element
    placeElement(row, col, element_id_to_replace)
    placeElement(row + gravity, col, element_id_target)

def placeElement(row, col, element):
    grid[row][col].element = element
    grid[row][col].temperature = element.temperature
    pygame.draw.rect(window, element.color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

def radiusTemp(row, col, radius):
    element = grid[row][col].element
    for i in range(-radius, radius):
        for j in range(-radius, radius):
            if 0 <= row + i < ROWS and 0 <= col + j < COLS:
                grid[row + i][col + j].temperature = (grid[row + i][col + j].temperature + element.temperature) / 2

def updatePositionElements(row, col, gravityLevel):
    actualElementId = grid[row][col].element
    placeElement(row, col, void)
    placeElement(row + gravityLevel, col, actualElementId)


def getElementById(id):
    for element in listElement:
        if element.id == id:
            return element


def refresh():
    # Draw cells
    for row in range(ROWS):
        for col in range(COLS):
            element = grid[row][col].element
            placeElement(row, col, element)


current_cell = None

while True:
    updateElements()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        ui_manager.process_events(event)

        if event.type == pygame.MOUSEMOTION:
            # Get mouse position
            pos = pygame.mouse.get_pos()
            # Convert mouse position to cell indices
            col = pos[0] // CELL_SIZE
            row = pos[1] // CELL_SIZE
            # Check if mouse button is down and update grid
            if mouse_down and 0 <= row < ROWS and 0 <= col < COLS:
                element_name = dropdown_menu.selected_option
                backgroundColor = 0
                if element_name == 'Sand':
                    backgroundColor = 1
                elif element_name == 'Rock':
                    backgroundColor = 2
                elif element_name == 'Grass':
                    backgroundColor = 3
                elif element_name == 'Void':
                    backgroundColor = 0
                elif element_name == 'Water':
                    backgroundColor = 4
                elif element_name == 'Lava':
                    backgroundColor = 5
                elif element_name == 'Vapor':
                    backgroundColor = 6
                elif element_name == 'Helium':
                    backgroundColor = 7
                elif element_name == 'Ice':
                    backgroundColor = 8
                if (row, col) != current_cell:
                    grid[row][col].element = getElementById(backgroundColor)
                    refresh()
                current_cell = (row, col)
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_down = True  # Set mouse button status to down

        if event.type == pygame.MOUSEBUTTONUP:
            mouse_down = False  # Set mouse button status to up

    if reset_button.check_pressed():
        window.fill(VOID)
        for row in range(ROWS):
            for col in range(COLS):
                grid[row][col] = Cell()
        refresh()

    # Update pygame_gui.UIManager with time_delta
    time_delta = clock.tick(60) / 1000.0
    ui_manager.update(time_delta)

    # Draw pygame_gui elements
    ui_manager.draw_ui(window)

    # Update display
    pygame.display.flip()
