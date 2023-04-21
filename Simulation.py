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

LAYER_TEMP = 0

VOID = (0, 0, 0)
SAND = (255, 255, 0)
ROCK = (128, 128, 128)
GRASS = (0, 255, 0)
WATER = (0, 0, 255)
LAVA = (255, 0, 0)
VAPOR = (0, 255, 255)
HELIUM = (0, 255, 128)
ICE = (0, 180, 180)
STEEL = (200, 200, 200)

BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
GREEN = (0, 255, 0)
YELLOW = (0, 0, 0)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

void = Element(VOID, 0, 0, "Void", 0, -1)
sand = Element(SAND, 1, 1, "Sand", 0, 1)
rock = Element(ROCK, 0, 2, "Rock", 0, 0)
grass = Element(GRASS, 0, 3, "Grass", 0, 0)
water = Element(WATER, 1, 4, "Water", 23, 1)
lava = Element(LAVA, 1, 5, "Lava", 1200, 1)
vapor = Element(VAPOR, -1, 6, "Vapor", 100, 1)
helium = Element(HELIUM, 1, 7, "Helium", -273, 1)
ice = Element(ICE, 0, 8, "Ice", -15)
steel = Element(ROCK, 0, 9, "Steel", 0)

listElement = [void, sand, rock, grass, water, lava, vapor, helium, ice, steel]

# Set up clock
clock = pygame.time.Clock()
FPS = 60  # Frames per second

# Initialize pygame
pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulation")

# Create a pygame_gui.UIManager
ui_manager = pygame_gui.UIManager((WIDTH, HEIGHT))

reset_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((20, 150), (100, 40)),
                                            text='Reset',
                                            manager=ui_manager
                                            )
layer_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((20, 100), (100, 40)),
                                            text='Layer',
                                            manager=ui_manager
                                        )


dropdown_menu = pygame_gui.elements.UIDropDownMenu(
    # get All name of item where are int the elementList
    options_list=[element.name for element in listElement],
    starting_option='Lava',
    relative_rect=pygame.Rect((20, 200), (100, 30)),
    manager=ui_manager)

# Create a 2D list and create Cell object at each
grid = [[Cell() for col in range(COLS)] for row in range(ROWS)]

# Keep track of mouse button status
mouse_down = False


def smoothTemperature(row, col):
    radius = 4
    tempatures = []

    if grid[row][col].element.id == 0:
        grid[row][col].temperature = int((grid[row][col].temperature + 0) / 2)
    else:
        for i in range(-radius, radius + 1):
            for j in range(-radius, radius + 1):
                if 0 <= row + i < ROWS and 0 <= col + j < COLS:
                    tempatures.append(grid[row + i][col + j].temperature)
        grid[row][col].temperature = grid[row][col].element.temperature + sum(tempatures) / len(tempatures)


def updateTemperature(row, col):
    if grid[row][col] != 0:
        smoothTemperature(row, col)


def updateElements():
    # Balayage bas vers haut
    for row in reversed(range(ROWS - 1)):
        for col in range(COLS):
            if LAYER_TEMP == 1:
                draw_cell(window, grid[row][col].temperature, row, col, CELL_SIZE)
            # Floor
            if grid[row][col].element.gravity == 1:
                updateTemperature(row, col)
                if grid[row + 1][col].element.id == 0:
                    updatePositionElements(row, col, 1)

                if grid[row][col].element.id == 4:
                     radiusTemp(row, col, 5)
                if grid[row][col].element.id == 7:
                    radiusTemp(row, col, 5)
                if grid[row][col].element.id == 5:
                    radiusTemp(row, col, 5)
                if grid[row][col].element.id == 6:
                    radiusTemp(row, col, 5)
                if grid[row][col].element.id == 8:
                    radiusTemp(row, col, 2)

            if grid[row][col].temperature != 0:
                smoothTemperature(row, col)
                temperatureCheck(row, col)

    # Balayage haut vers bas
    for row in range(ROWS - 1):
        for col in range(COLS):
            if grid[row][col].element.gravity == -1:
                updateTemperature(row, col)
                if grid[row - 1][col].element.gravity == 1 or grid[row - 1][col].element.id == 0:
                    permutationElement(row, col, grid[row][col].element.gravity)
    time.sleep(1 / FPS)


def temperatureCheck(row, col):
    # Transformation
    if grid[row][col].temperature > 100:
        if grid[row][col].element.id == 4:  # water
            placeElement(row, col, vapor)
        if grid[row][col].element.id == 8: # ice
            placeElement(row, col, water)
    if grid[row][col].temperature < 0:
        if grid[row][col].element.id == 4:  # water
            placeElement(row, col, ice)

    if grid[row][col].temperature < 50:
        if grid[row][col].element.id == 6:  # vapor
            placeElement(row, col, water)

    if grid[row][col].temperature <= 500:
        if grid[row][col].element.id == 5:  # lava
            placeElement(row, col, rock)


def permutationElement(row, col, gravity):
    element_id_to_replace = grid[row + gravity][col].element
    element_id_target = grid[row][col].element
    placeElement(row, col, element_id_to_replace)
    placeElement(row + gravity, col, element_id_target)


def placeElement(row, col, element):
    grid[row][col].element = element
    grid[row][col].temperature = (element.temperature + grid[row][col].temperature) / 2
    pygame.draw.rect(window, element.color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    temperatureCheck(row, col)
    smoothTemperature(row, col)


def radiusTemp(row, col, radius):
    for i in range(row - radius, row + radius + 1):
        for j in range(col - radius, col + radius + 1):
            distance = (i - row) ** 2 + (j - col) ** 2
            if distance <= radius ** 2:
                distance_factor = 1 - ((i - row) ** 2 + (j - col) ** 2) ** 0.5 / radius
                grid[i][j].temperature = int(
                    (int(grid[row][col].temperature * distance_factor) + grid[i][j].temperature) / 2)




def updatePositionElements(row, col, gravityLevel):
    actualElementId = grid[row][col].element
    placeElement(row, col, void)
    placeElement(row + gravityLevel, col, actualElementId)
    temperatureCheck(row + gravityLevel, col)


def lerp(c1, c2, t):
    r = int(c1[0] + (c2[0] - c1[0]) * t)
    g = int(c1[1] + (c2[1] - c1[1]) * t)
    b = int(c1[2] + (c2[2] - c1[2]) * t)
    if r < 0:
        r = 0
    elif r > 255:
        r = 255
    if g < 0:
        g = 0
    elif g > 255:
        g = 255
    if b < 0:
        b = 0
    elif b > 255:
        b = 255
    return (r, g, b)


# Dessiner les cellules en fonction de leur température
def draw_cell(window, temperature, i, j, CELL_SIZE):
    if temperature < -273.15:
        color = WHITE
    elif temperature < -250:
        color = lerp(BLUE, CYAN, (temperature + 250) / 200)
    elif temperature < -50:
        color = lerp(CYAN, GREEN, (temperature + 50) / 200)
    elif temperature < 0:
        color = lerp(GREEN, YELLOW, temperature / 50)
    elif temperature < 100:
        color = lerp(YELLOW, ORANGE, temperature / 100)
    elif temperature < 1000:
        color = lerp(ORANGE, RED, (temperature - 100) / 900)
    else:
        color = RED
    pygame.draw.rect(window, color, (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))


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

for i in range(COLS):
    placeElement(50, i, rock)

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
                elementPlaced = None

                #search for the element in the list by name
                for element in listElement:
                    if element.name == element_name:
                        elementPlaced = element

                if (row, col) != current_cell:
                    grid[row][col].element = elementPlaced
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
        if LAYER_TEMP == 0:
            refresh()

    if layer_button.check_pressed():
        LAYER_TEMP = 1 - LAYER_TEMP
        refresh()

    # Update pygame_gui.UIManager with time_delta
    time_delta = clock.tick(60) / 1000.0
    ui_manager.update(time_delta)

    # Draw pygame_gui elements
    ui_manager.draw_ui(window)

    # Update display
    pygame.display.flip()
