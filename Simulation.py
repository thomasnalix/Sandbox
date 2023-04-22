import pygame
import sys
import pygame_gui
import time

from Transformation import Transformation
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
AZOTE = (0, 255, 128)
ICE = (0, 180, 180)
STEEL = (200, 200, 200)
AZOTE_GAZ = (250, 250, 255)

BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)

void = Element(VOID, 0, 0, "Void", 0, -1, 0, 1)
sand = Element(SAND, 1, 1, "Sand", 0, 1, 2, 1)
rock = Element(ROCK, 0, 2, "Rock", 0, 0, 10, 1)
grass = Element(GRASS, 0, 3, "Grass", 0, 0, 100, 1)
water = Element(WATER, 1, 4, "Water", 23, 10, 10, 1.01)
lava = Element(LAVA, 1, 5, "Lava", 2000, 1, 5, 1.0001)
vapor = Element(VAPOR, -1, 6, "Vapor", 100, 1, 5, 1.01)
azote = Element(AZOTE, 1, 7, "Azote", -273, 1, 5, 1.01)
ice = Element(ICE, 0, 8, "Ice", -15, 0, 2, 1.01)
steel = Element(STEEL, 0, 9, "Steel", 0, 0, 100, 1)
azote_gaz = Element(AZOTE_GAZ, -1, 10, "Azote gaz", 0, 1, 5, 1.1)

trans_vapor = Transformation(0, 100, water)
trans_ice = Transformation(-275, 0, water)
trans_waterV = Transformation(100, 100000, vapor)
trans_waterI = Transformation(-275, 0, ice)
trans_rock = Transformation(1000, 10000000, lava)
trans_lava = Transformation(-275, 1000, rock)
trans_sand = Transformation(1000, 1000000, lava)
trans_azote = Transformation(0, 100000, azote_gaz)

rock.transform = [trans_rock]
sand.transform = [trans_sand]
lava.transform = [trans_lava]
water.transform = [trans_waterV, trans_waterI]
ice.transform = [trans_ice]
vapor.transform = [trans_vapor]
azote.transform = [trans_azote]

listElement = [void, sand, rock, grass, water, lava, vapor, azote, ice, steel]

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
grid = [[Cell(void.copy()) for col in range(COLS)] for row in range(ROWS)]

# Keep track of mouse button status
mouse_down = False


def smoothTemperature(row, col):
    radius = 1
    tempatures = []
    grid[row][col].element.temperature /= grid[row][col].element.dissipation
    if grid[row][col].element.id == 0:
        grid[row][col].temperature = (grid[row][col].temperature + 0) / 2
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

                # Calcul propagation of heat
                if grid[row][col].element.id in [4, 7, 5, 6]:
                    radiusTemp(row, col, 4)

            # Calcul heat propagation for ice
            if grid[row][col].element.gravity == 0:
                if grid[row][col].element.id == 8:
                    radiusTemp(row, col, 3)

            # For all element where temperature is not 0, we smooth the temperature by the average of the temperature of the element around
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
    adjacent_temp = 0
    # top, left, right, bottom AND check if element is not out of range
    if 0 <= row - 1 < ROWS:
        adjacent_temp += grid[row - 1][col].temperature
    if 0 <= col - 1 < COLS:
        adjacent_temp += grid[row][col - 1].temperature
    if 0 <= col + 1 < COLS:
        adjacent_temp += grid[row][col + 1].temperature
    if 0 <= row + 1 < ROWS:
        adjacent_temp += grid[row + 1][col].temperature
    adjacent_temp += grid[row][col].temperature

    average_temp = adjacent_temp / 5
    element = grid[row][col].element
    if element.transform is not None:
        for transformation in element.transform:
            if transformation.temperature_min < average_temp < transformation.temperature_max:
                transform(transformation.element.copy(), row, col)


def transform(final_element, row, col):
    durability_factor = 0.1
    if grid[row][col].temperature > 0:
        durability_factor = (1 - max(min(100 / grid[row][col].temperature, 0.1), 0.9))
    elif grid[row][col].temperature < 0:
        durability_factor = (1 - max(min(abs(100 / grid[row][col].temperature), 0.1), 0.9))
    grid[row][col].element.durability -= durability_factor
    if grid[row][col].element.durability <= 0:
        grid[row][col].element = grid[row][col].element.changeElement(final_element, element.temperature/1.2)
        pygame.draw.rect(window, grid[row][col].element.color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))


def permutationElement(row, col, gravity):
    element_to_replace = grid[row + gravity][col].element
    element_target = grid[row][col].element
    placeElement(row, col, element_to_replace)
    placeElement(row + gravity, col, element_target)


def placeElement(row, col, element):
    grid[row][col].element = element
    grid[row][col].temperature = (element.temperature + grid[row][col].temperature) / 2
    pygame.draw.rect(window, element.color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    temperatureCheck(row, col)
    smoothTemperature(row, col)


def updatePositionElements(row, col, gravity_level):
    element_actual = grid[row][col].element
    element_target = grid[row + gravity_level][col].element
    placeElement(row, col, element_target)
    placeElement(row + gravity_level, col, element_actual)
    temperatureCheck(row + gravity_level, col)


def radiusTemp(row, col, radius):
    for i in range(row - radius, row + radius + 1):
        for j in range(col - radius, col + radius + 1):
            distance = (i - row) ** 2 + (j - col) ** 2
            if distance <= radius ** 2:
                distance_factor = 1 - ((i - row) ** 2 + (j - col) ** 2) ** 0.5 / radius
                grid[i][j].temperature = (grid[row][col].temperature * distance_factor + grid[i][j].temperature) / 2


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
    return r, g, b


# Dessiner les cellules en fonction de leur température
def draw_cell(window, temperature, i, j, CELL_SIZE):
    if temperature < -250:
        color = lerp(CYAN, BLUE, (temperature + 250) / -200)
    elif temperature < -50:
        color = lerp(GREEN, CYAN, (temperature + 50) / -50)
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


current_cell = None
current_element = lava

for i in range(COLS):
    placeElement(46, i, rock)
    placeElement(50, i, steel)
    placeElement(51, i, steel)
    placeElement(52, i, steel)
    placeElement(53, i, steel)
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

                if (row, col) != current_cell:
                    placeElement(row, col, current_element)
                current_cell = (row, col)

        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_down = True  # Set mouse button status to down

        if event.type == pygame.MOUSEBUTTONUP:
            mouse_down = False  # Set mouse button status to up

    # Reset button
    if reset_button.check_pressed():
        window.fill(VOID)
        for row in range(ROWS):
            for col in range(COLS):
                grid[row][col] = Cell(void.copy())

    # Layer button
    if layer_button.check_pressed():
        LAYER_TEMP = 1 - LAYER_TEMP
        for row in range(ROWS):
            for col in range(COLS):
                pygame.draw.rect(window, grid[row][col].element.color,
                                 (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # if selection was changed, update the element
    if dropdown_menu.selected_option != current_element:
        current_element = dropdown_menu.selected_option
        for element in listElement:
            if element.name == current_element:
                current_element = element.copy()
                break

    # Update pygame_gui.UIManager with time_delta
    time_delta = clock.tick(60) / 1000.0
    ui_manager.update(time_delta)

    # Draw pygame_gui elements
    ui_manager.draw_ui(window)

    # Update display
    pygame.display.flip()
