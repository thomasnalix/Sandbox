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
WATER = (0, 0, 255)
LAVA = (255, 0, 0)
VAPOR = (0, 255, 255)
AZOTE = (0, 255, 128)
ICE = (0, 180, 180)
STEEL = (200, 200, 200)
AZOTE_GAZ = (128, 255, 128)

# Elements
void = Element(VOID, None, "Void", 0, 'VOID', 0, 1, 0)
sand = Element(SAND, 1, "Sand", 0, 'FALLING', 2, 1, 0)
rock = Element(ROCK, 0, "Rock", 0, 'SOLID', 10, 1, 0)
water = Element(WATER, 1, "Water", 23, 'FALLING', 10, 1.01, 2)
lava = Element(LAVA, 1, "Lava", 2000, 'FALLING', 1, 1.001, 4)
vapor = Element(VAPOR, -1, "Vapor", 100, 'FALLING', 5, 1.01, 4)
azote = Element(AZOTE, 1, "Azote", -273, 'FALLING', 5, 1.001, 4)
ice = Element(ICE, 0, "Ice", -15, 'SOLID', 0, 1.01, 2)
steel = Element(STEEL, 0, "Steel", 0, 'SOLID', 100, 1, 0)
azote_gaz = Element(AZOTE_GAZ, -1, "Azote gaz", 0, 'FALLING', 5, 1.1, 0)

# Transformations
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

# Menu items
listElement = [void, sand, rock, water, lava, vapor, azote, ice, steel, azote_gaz]

# Set up clock
clock = pygame.time.Clock()
FPS = 60  # Frames per second

# Initialize pygame
pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Simulation")

ui_manager = pygame_gui.UIManager((WIDTH, HEIGHT))

reset_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((20, 150), (100, 40)),
                                            text='Reset',
                                            manager=ui_manager
                                            )
layer_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect((20, 100), (100, 40)),
                                            text='Thermic',
                                            manager=ui_manager
                                            )
dropdown_menu = pygame_gui.elements.UIDropDownMenu(options_list=[element.name for element in listElement],
                                                   starting_option='Lava',
                                                   relative_rect=pygame.Rect((20, 200), (100, 30)),
                                                   manager=ui_manager)

# Create a 2D list and create Cell object at each
grid = [[Cell(void.copy()) for col in range(COLS)] for row in range(ROWS)]

# Keep track of mouse button status
mouse_down = False


def smooth_temperature(row, col):
    radius = 1
    tempatures = []

    grid[row][col].temperature /= grid[row][col].element.dissipation
    grid[row][col].element.temperature /= grid[row][col].element.dissipation
    if grid[row][col].element.type == 'VOID':
        grid[row][col].temperature = (grid[row][col].temperature + 0) / 2
    else:
        for i in range(-radius, radius + 1):
            for j in range(-radius, radius + 1):
                if 0 <= row + i < ROWS and 0 <= col + j < COLS:
                    tempatures.append(grid[row + i][col + j].temperature)
        grid[row][col].temperature = grid[row][col].element.temperature + sum(tempatures) / len(tempatures)


def update_temperature(row, col):
    if grid[row][col] != 0:
        smooth_temperature(row, col)
        temperature_check(row, col)


def update_elements():
    # Balayage from bottom to top
    for row in reversed(range(ROWS - 1)):
        for col in range(COLS):

            # Thermic layer
            if LAYER_TEMP == 1:
                draw_cell(window, grid[row][col].temperature, row, col, CELL_SIZE)

            # Floor
            if grid[row][col].element.gravity == 1:
                if grid[row + 1][col].element.gravity in [-1, None]:
                    update_position_elements(row, col, 1)

            radius_temp(row, col, grid[row][col].element.propagation)
            update_temperature(row, col)

    # Balayage from top to bottom
    for row in range(ROWS - 1):
        for col in range(COLS):
            if grid[row][col].element.gravity == -1:
                update_temperature(row, col)
                if grid[row - 1][col].element.gravity == 1 or grid[row - 1][col].element.gravity in [-1, None]:
                    update_position_elements(row, col, grid[row][col].element.gravity)
    time.sleep(1 / FPS)


def temperature_check(row, col):
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
    if element.transform is None:
        return
    for transformation in element.transform:
        if transformation.temperature_min < average_temp < transformation.temperature_max:
            transform_element(transformation.element.copy(), row, col)


def transform_element(final_element, row, col):
    durability_factor = 0.1
    temperature = 0
    if grid[row][col].temperature > 0:
        durability_factor = (1 - max(min(100 / grid[row][col].temperature, 0.1), 0.9))
        temperature = max(grid[row][col].element.temperature / 1.2, 0)
    elif grid[row][col].temperature < 0:
        durability_factor = (1 - max(min(abs(100 / grid[row][col].temperature), 0.1), 0.9))
        temperature = min(grid[row][col].element.temperature / 1.2, 0)

    grid[row][col].element.durability -= durability_factor
    if grid[row][col].element.durability <= 0:
        grid[row][col].element = grid[row][col].element.change_element(final_element, temperature)
        pygame.draw.rect(window, grid[row][col].element.color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))


def place_element(row, col, element):
    grid[row][col].element = element
    grid[row][col].temperature = (element.temperature + grid[row][col].temperature) / 2
    pygame.draw.rect(window, element.color, (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    temperature_check(row, col)
    smooth_temperature(row, col)


def update_position_elements(row, col, gravity_level):
    element_actual = grid[row][col].element
    element_target = grid[row + gravity_level][col].element
    place_element(row, col, element_target)
    place_element(row + gravity_level, col, element_actual)
    temperature_check(row + gravity_level, col)


def radius_temp(row, col, radius):
    if radius == 0:
        return
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
    r = max(0, min(r, 255))
    g = max(0, min(g, 255))
    b = max(0, min(b, 255))
    return r, g, b


# Dessiner les cellules en fonction de leur température
def draw_cell(window, temperature, i, j, cell_size):
    if temperature < -250:
        color = lerp((0, 0, 255), (0, 255, 255), (temperature + 250) / -750)
    elif temperature < -50:
        color = lerp((0, 255, 255), (0, 255, 0), (temperature + 50) / -200)
    elif temperature < 0:
        color = lerp((0, 255, 0), (255, 255, 0), temperature / -50)
    elif temperature < 100:
        color = lerp((255, 255, 0), (255, 165, 0), temperature / 100)
    elif temperature < 1000:
        color = lerp((255, 165, 0), (255, 0, 0), (temperature - 100) / 900)
    else:
        color = (255, 0, 0)
    pygame.draw.rect(window, color, (j * cell_size, i * cell_size, cell_size, cell_size))


current_cell = None
current_element = lava

# Initialisation of preadefined elements
for i in range(COLS):
    place_element(46, i, rock)
    place_element(50, i, steel)
    place_element(51, i, steel)
    place_element(52, i, steel)
    place_element(53, i, steel)

while True:
    update_elements()
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
                    place_element(row, col, current_element)
                current_cell = (row, col)
                # print temperature of the cell of each row and column

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
