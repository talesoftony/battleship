
"""
Battleship362
Sam
Kyle
Tony
"""

# Imports
import pygame, sys, random
from pygame.locals import *
from globals import *

def main():
    """
    Setup of game components
    """
    global WINDOWSURFACE, GLOBALCLOCK, FONTSIZESMALL, LOCINFO, INFORECT, LOCRESET, RESETRECT, FONTSIZELARGE, EFFECTS

    pygame.init()
    GLOBALCLOCK = pygame.time.Clock()
    WINDOWSURFACE = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Battleship362')

    # FONTS
    FONTSIZESMALL = pygame.font.Font('../Fonts/slkscr.ttf', 20)
    FONTSIZELARGE = pygame.font.Font('../Fonts/slkscr.ttf', 50)

    # BUTTONS
    LOCINFO = FONTSIZESMALL.render("HELP", True, COLTEXT)
    INFORECT = LOCINFO.get_rect()
    INFORECT.topleft = (WINDOWWIDTH - 300, WINDOWHEIGHT - 750)
    LOCRESET = FONTSIZESMALL.render("RESET", True, COLTEXT)
    RESETRECT = LOCRESET.get_rect()
    RESETRECT.topleft = (WINDOWWIDTH - 500, WINDOWHEIGHT - 750)

    # IMAGES, can add more in and cycle through
    EFFECTS = [pygame.image.load("../Images/explosion.png")]

    # Run displays, can be changed from while True to while not exit
    game_intro_display()
    while True:
        winner = main_game_loop()  # Game loop and pass through winning player
        game_end_display(winner)  # Display end screen


def main_game_loop():
    """
    Runs game loop
    """

    # Tiles cleared from fog of war
    shown_user_tiles = make_board(False)
    shown_opponent_tiles = make_board(False)

    # Create game boards
    user_board = make_board(None)
    opponent_board = make_board(None)

    shipSet = ["battleship", "cruiser", "destroyer", "submarine"]

    # Add ships to each board
    user_board = random_shipset_placement(user_board, shipSet)
    opponent_board = random_shipset_placement(opponent_board, shipSet)

    # Tuple of mouse position
    mouse_x_pos, mouse_y_pos = 0, 0

    while True:
        # Background, Buttons, Boards
        WINDOWSURFACE.fill(COLBACKGROUND)
        WINDOWSURFACE.blit(LOCINFO, INFORECT)
        WINDOWSURFACE.blit(LOCRESET, RESETRECT)
        draw_boards(user_board, shown_user_tiles, 1)
        draw_boards(opponent_board, shown_opponent_tiles, 2)

        mouse_clicked = False

        check_for_quit()

        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                if INFORECT.collidepoint(event.pos):  # Access info
                    WINDOWSURFACE.fill(COLBACKGROUND)
                    info_display()
                elif RESETRECT.collidepoint(event.pos):  # Reset game
                    main()
                else:
                    mouse_x_pos, mouse_y_pos = event.pos
                    mouse_clicked = True  # Click mouse at position
            elif event.type == MOUSEMOTION:
                mouse_x_pos, mouse_y_pos = event.pos  # update mouse pos

        tile_x_pos, tile_y_pos = find_tile_at(mouse_x_pos, mouse_y_pos)
        if tile_x_pos is not None and tile_y_pos is not None: # Click mouse on tile for different states
            if not shown_user_tiles[tile_x_pos][tile_y_pos]:  # Has no fog of war
                mouseover_highlight(tile_x_pos, tile_y_pos)
            if not shown_user_tiles[tile_x_pos][tile_y_pos] and mouse_clicked:  # Has fog of war
                reveal_tile_animation(user_board, [(tile_x_pos, tile_y_pos)])
                shown_user_tiles[tile_x_pos][tile_y_pos] = True # Remove fog of war
                if check_revealed_tile(user_board, [(tile_x_pos, tile_y_pos)]):  # Correct selection of ship
                    left, top = find_top_left_pos(tile_x_pos, tile_y_pos, 1)
                    effect_animation((left, top))
                    if check_for_win(user_board, shown_user_tiles):
                        return "USER"
                    if check_for_win(opponent_board, shown_opponent_tiles):
                        return "AI"
                ai_turn()

        pygame.display.update()
        GLOBALCLOCK.tick(GAMEFPS)


def ai_turn():
    """
    Function gives the AI their turn. Decides the tile to click through ai_find_tile.
    Clicks returned tile, reveals on board 2.
    Displays if the AI shot was a hit or miss.
    """
    ai_find_tile()


def ai_find_tile():
    """
    Chooses a random tile
    """


def make_board(entry_tile_value):
    """
    Creates y-tiles by x-tiles with an entry value passed in
    """
    entry_tiles = [[entry_tile_value] * BOARDYTILES for i in range(BOARDXTILES)]

    return entry_tiles


def effect_animation(tile_needs_effect):
    """
    Image loop for effect on a specific tile, will run multiple sprite png's
    """
    for image in EFFECTS:
        image = pygame.transform.scale(image, (TILESIZE + 50, TILESIZE + 50))
        WINDOWSURFACE.blit(image, tile_needs_effect)
        pygame.display.flip()
        GLOBALCLOCK.tick(EFFECTFPS)


def check_revealed_tile(board, tile):
    """
    Check if ship
    """
    return board[tile[0][0]][tile[0][1]] is not None


def reveal_tile_animation(board, tile_to_reveal):
    """
    Uncover tiles
    """
    for covered in range(TILESIZE, (-CLICKSPEED) - 1, -CLICKSPEED):  # Plays animation based on reveal speed
        draw_tile_surface(board, tile_to_reveal, covered)


def draw_tile_surface(board, tile, covered):
    """
    Updates tile image
    """
    left, top = find_top_left_pos(tile[0][0], tile[0][1], 1)
    if check_revealed_tile(board, tile):
        pygame.draw.rect(WINDOWSURFACE, COLSHIP, (left, top, TILESIZE, TILESIZE))
    else:
        pygame.draw.rect(WINDOWSURFACE, COLBACKGROUND, (left, top, TILESIZE, TILESIZE))
    if covered > 0:
        pygame.draw.rect(WINDOWSURFACE, COLTILE, (left, top, covered, TILESIZE))

    pygame.display.update()
    GLOBALCLOCK.tick(GAMEFPS)


def check_for_quit():
    """
    Quick check for pygame quit event
    """
    for event in pygame.event.get(QUIT):
        pygame.quit()
        sys.exit()


def check_for_win(board, revealed):
    """
    Checks current board state for winner, check if every tile with a ship is shown
    """
    for tile_x_pos in range(BOARDXTILES):
        for tile_y_pos in range(BOARDYTILES):
            if board[tile_x_pos][tile_y_pos] is not None and not revealed[tile_x_pos][tile_y_pos]:
                return False
    return True


def draw_boards(board, revealed, player):
    """
    Prints boards to window
    """
    if player is 1:
        for tile_x_pos in range(BOARDXTILES):
            for tile_y_pos in range(BOARDYTILES):
                left, top = find_top_left_pos(tile_x_pos, tile_y_pos, player)
                if not revealed[tile_x_pos][tile_y_pos]:
                    pygame.draw.rect(WINDOWSURFACE, COLTILE, (left, top, TILESIZE, TILESIZE))
                else:
                    if board[tile_x_pos][tile_y_pos] is not None:
                        pygame.draw.rect(WINDOWSURFACE, COLSHIP, (left, top, TILESIZE, TILESIZE))
                    else:
                        pygame.draw.rect(WINDOWSURFACE, COLBACKGROUND, (left, top, TILESIZE, TILESIZE))
    if player is 2:
        for tile_x_pos in range(BOARDXTILES):
            for tile_y_pos in range(BOARDYTILES):
                left, top = find_top_left_pos(tile_x_pos, tile_y_pos, player)
                if not revealed[tile_x_pos][tile_y_pos]:
                    if board[tile_x_pos][tile_y_pos] is not None:
                        pygame.draw.rect(WINDOWSURFACE, COLUSERSHIPS, (left, top, TILESIZE, TILESIZE))
                    else:
                        pygame.draw.rect(WINDOWSURFACE, COLTILE, (left, top, TILESIZE, TILESIZE))
                else:
                    if board[tile_x_pos][tile_y_pos] is not None:
                        pygame.draw.rect(WINDOWSURFACE, COLSHIP, (left, top, TILESIZE, TILESIZE))
                    else:
                        pygame.draw.rect(WINDOWSURFACE, COLBACKGROUND, (left, top, TILESIZE, TILESIZE))


def random_shipset_placement(board, ships):
    """
    Brute force placement of ships on a new board
    """
    new_board = board[:]
    ship_length = 0
    for ship in ships:

        valid_pos = False

        while not valid_pos:
            orientationisHorizontal = random.randint(0, 1)

            xStartpos = random.randint(0, 9)
            yStartpos = random.randint(0, 9)

            if 'destroyer' in ship:
                ship_length = 5
            elif 'cruiser' in ship:
                ship_length = 3
            elif 'battleship' in ship:
                ship_length = 4
            elif 'submarine' in ship:
                ship_length = 2

            # valid_pos set to true if ship placement is valid
            valid_pos, ship_coords = add_ship(new_board, xStartpos, yStartpos, orientationisHorizontal, ship_length, ship)

            if valid_pos:
                for coord in ship_coords:
                    new_board[coord[0]][coord[1]] = ship
    return new_board


def add_ship(board, xTile, yTile, orientationIsHorizontal, length, ship):
    """
    Ship placer
    """
    coords = []
    if orientationIsHorizontal:
        for i in range(length):
            if (i + xTile > 9) or (board[i + xTile][yTile] is not None) or has_adj(board, i + xTile, yTile, ship):
                return False, coords
            else:
                coords.append((i + xTile, yTile))
    else:
        for i in range(length):
            if (i + yTile > 9) or (board[xTile][i + yTile] is not None) or has_adj(board, xTile, i + yTile, ship):
                return False, coords
            else:
                coords.append((xTile, i + yTile))
    return True, coords


def has_adj(board, xTile, yTile, ship):
    """
    Checks for adjacent objects
    """
    for x in range(xTile - 1, xTile + 2):
        for y in range(yTile - 1, yTile + 2):
            if (x in range(10)) and (y in range(10)) and (board[x][y] not in (ship, None)):
                return True
    return False


def find_top_left_pos(tile_x_pos, tile_y_pos, player):
    """
    Find tile of top left corner
    """
    offset = 40
    if player is 1:
        left = tile_x_pos * TILESIZE + BOARDONEXPOINT + offset
        top = tile_y_pos * TILESIZE + BOARDONEYPOINT + offset
    if player is 2:
        left = tile_x_pos * TILESIZE + BOARDTWOXPOINT + offset
        top = tile_y_pos * TILESIZE + BOARDTWOYPOINT + offset
    return left, top


def find_tile_at(x, y):
    """
    Returns tile at a position
    """
    for tile_x_pos in range(BOARDXTILES):
        for tile_y_pos in range(BOARDYTILES):
            left, top = find_top_left_pos(tile_x_pos, tile_y_pos, 1)
            tile_rect = pygame.Rect(left, top, TILESIZE, TILESIZE)
            if tile_rect.collidepoint(x, y):
                return tile_x_pos, tile_y_pos
    return None, None


def mouseover_highlight(tile_x_pos, tile_y_pos):
    """
    Highlights current tile
    """
    left, top = find_top_left_pos(tile_x_pos, tile_y_pos, 1)
    pygame.draw.rect(WINDOWSURFACE, COLHIGHLIGHT, (left, top, TILESIZE, TILESIZE), 2)


def info_display():
    """
    Display info  screen
    """
    infoSurface, infoRectangle = create_writable_object('Insert any instructions here', FONTSIZESMALL, COLTEXT)
    infoRectangle.topleft = (TEXTPOS, TEXTSIZE + 60)
    WINDOWSURFACE.blit(infoSurface, infoRectangle)

    infoSurface, infoRectangle = create_writable_object('BATTLESHIP', FONTSIZESMALL, COLTEXT)
    infoRectangle.topleft = (TEXTPOS, TEXTSIZE + 120)
    WINDOWSURFACE.blit(infoSurface, infoRectangle)

    infoSurface, infoRectangle = create_writable_object('Sink your opponents fleet!', FONTSIZESMALL, COLTEXT)
    infoRectangle.topleft = (TEXTPOS, TEXTSIZE + 150)
    WINDOWSURFACE.blit(infoSurface, infoRectangle)

    while check_for_key_up() is None:
        pygame.display.update()
        GLOBALCLOCK.tick()


def check_for_key_up():
    """
    Only returns keyup events
    """
    for event in pygame.event.get([KEYDOWN, KEYUP, MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION]):
        if event.type in (KEYDOWN, MOUSEBUTTONUP, MOUSEBUTTONDOWN, MOUSEMOTION):
            continue
        return event.key
    return None


def create_writable_object(text, font, color):
    """
    Easy print to screen function returns surface, rectangle
    """
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def game_end_display(winner):
    """
    Displays end screen
    """
    WINDOWSURFACE.fill(COLBACKGROUND)

    menuSurface, menuRectangle = create_writable_object('Oh yeah!', FONTSIZELARGE, COL3DTEXT)
    menuRectangle.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    WINDOWSURFACE.blit(menuSurface, menuRectangle)

    menuSurface, menuRectangle = create_writable_object('Oh yeah!', FONTSIZELARGE, COLTEXT)
    menuRectangle.center = (int(WINDOWWIDTH / 2) - 3, int(WINDOWHEIGHT / 2) - 5)
    WINDOWSURFACE.blit(menuSurface, menuRectangle)

    menuSurface, menuRectangle = create_writable_object(str(winner) + ' is the Winner', FONTSIZELARGE, COL3DTEXT)
    menuRectangle.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2 + 50))
    WINDOWSURFACE.blit(menuSurface, menuRectangle)

    menuSurface, menuRectangle = create_writable_object(str(winner) + ' is the Winner', FONTSIZELARGE, COLTEXT)
    menuRectangle.center = (int(WINDOWWIDTH / 2) - 3, int(WINDOWHEIGHT / 2 + 50) - 5)
    WINDOWSURFACE.blit(menuSurface, menuRectangle)

    pressKeySurf, pressKeyRect = create_writable_object('Press a key to try to play again', FONTSIZESMALL, COLTEXT)
    pressKeyRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 100)
    WINDOWSURFACE.blit(pressKeySurf, pressKeyRect)

    while check_for_key_up() is None:
        pygame.display.update()
        GLOBALCLOCK.tick()

def game_intro_display():
    """
    Displays intro screen
    """

    WINDOWSURFACE.fill(COLBACKGROUND)

    menuSurface, menuRectangle = create_writable_object('Welcome!', FONTSIZELARGE, COL3DTEXT)
    menuRectangle.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2 - 200))
    WINDOWSURFACE.blit(menuSurface, menuRectangle)

    menuSurface, menuRectangle = create_writable_object('Welcome!', FONTSIZELARGE, COLTEXT)
    menuRectangle.center = (int(WINDOWWIDTH / 2) - 3, int(WINDOWHEIGHT / 2 - 200) - 5)
    WINDOWSURFACE.blit(menuSurface, menuRectangle)

    menuSurface, menuRectangle = create_writable_object('Lets Play Battleship.', FONTSIZELARGE, COL3DTEXT)
    menuRectangle.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2 - 50))
    WINDOWSURFACE.blit(menuSurface, menuRectangle)

    menuSurface, menuRectangle = create_writable_object('Lets Play Battleship.', FONTSIZELARGE, COLTEXT)
    menuRectangle.center = (int(WINDOWWIDTH / 2) - 3, int(WINDOWHEIGHT / 2 - 50) - 5)
    WINDOWSURFACE.blit(menuSurface, menuRectangle)

    pressKeySurf, pressKeyRect = create_writable_object('Press any key to play', FONTSIZESMALL, COLTEXT)
    pressKeyRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 100)
    WINDOWSURFACE.blit(pressKeySurf, pressKeyRect)

    while check_for_key_up() is None:
        pygame.display.update()
        GLOBALCLOCK.tick()


if __name__ == "__main__":
    main()