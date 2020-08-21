import pygame
import sys
from random import randint
from time import time
from copy import deepcopy
from math import cos, sin, pi
from textwrap import TextWrapper


pygame.mixer.pre_init(buffer=10)
pygame.init()

class Squares:
    # holds all non_moving, fixed squares
    square_list = []  # contains dicts for each square {pos, length, colour}

    def __init__(self, width, no):
        self.length = width//no

    @classmethod
    def draw(cls, win):
        for square in cls.square_list:
            pygame.draw.rect(win, (0, 0, 0), (square['pos'][0], square['pos'][1], square['length'], square['length']))
            pygame.draw.rect(win, square['colour'],
                             (square['pos'][0]+2, square['pos'][1]+2, square['length']-4, square['length']-4))

    @classmethod
    def check_line(cls, line_no, no):
        # check if the given line is filled
        line_sq = list(filter(None, [square if square['pos'][1] == line_no else None for square in cls.square_list]))
        if len(line_sq) == no:
            return line_sq

    @classmethod
    def del_square(cls, line_sq, line_no):
        global delete
        sound_lib['delete'].play()
        for sq in line_sq:
            cls.square_list.remove(sq)
        for square in cls.square_list:
            if square['pos'][1] < line_no:
                square['pos'][1] += square['length']

    @classmethod
    def get_max(cls, x):
        # returns y-coordinate of highest block in a given column
        return max([square[1] if square[0] == x else 0 for square in cls.square_list['pos']])

class Blocks(Squares):
    # holds current, moving block, and the next 2 blocks to come (choices)
    block_names = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']
    choices = []

    def __init__(self, width, no, index):
        super().__init__(width, no)
        self.name = Blocks.choices[index]
        self.shape = self.get_shape(index, no, width)
        self.dir = (0, 0)
        self.projection = deepcopy(self.shape)
        self.collisions = set()  # tracks all the directions cur block has has collided in
        self.projection_collisions = set()  # tracks all the directions projection has has collided in
        self.rotate_sound = sound_lib['rotate']
        self.left, self.right, self.down = False, False, False

    @classmethod
    def get_choice(cls):
        while len(cls.choices) < 3:
            cls.choices.append(cls.block_names[randint(0, len(Blocks.block_names) - 1)])

    def get_shape(self, index, no, width):
        # returns a list of 4 coordinates for the 4 squares which makes up the block
        l = self.length
        mid = l * (no // 2)
        if index != 0:
            width = width+ 20  # translates blocks in side panel to the right a little
        if self.name == 'I':
            self.colour = (64, 224, 208)  # turquoise
            if index == 0:
                return [[mid - 2*l, 0], [mid - l, 0], [mid, 0], [mid + l, 0]]
            return [[width, 100*index*1.2], [width + l, 100*index*1.2], [width + 2*l, 100*index*1.2], [width + 3*l, 100*index*1.2]]
        if self.name == 'J':
            self.colour = (0, 0, 200)  # blue
            if index == 0:
                return [[mid, 0], [mid, l], [mid, 2*l], [mid - l, 2*l]]
            return [[width, 100*index*1.2], [width, 100*index*1.2 + l], [width + l, 100*index*1.2 + l], [width + 2*l, 100*index*1.2 + l]]
        if self.name == 'L':
            self.colour = (0, 50, 0)  # forest green
            if index == 0:
                return [[mid - l, 0], [mid - l, l], [mid - l, 2*l], [mid, 2*l]]
            return [[width, 100*index*1.2], [width, 100*index*1.2 + l], [width + l, 100*index*1.2 + l], [width + 2*l, 100*index*1.2 + l]]
        if self.name == 'O':
            self.colour = (255, 255, 0)  # yellow
            if index == 0:
                return [[mid - l, 0], [mid, 0], [mid - l, l], [mid, l]]
            return [[width, 100*index*1.2], [width, 100*index*1.2 + l], [width + l, 100*index*1.2], [width + l, 100*index*1.2 + l]]
        if self.name == 'S':
            self.colour = (200, 0, 0)  # red
            if index == 0:
                return [[mid - l, 0], [mid, 0], [mid - l, l], [mid - 2*l, l]]
            return [[width + 2*l, 100*index*1.2], [width + l, 100*index*1.2], [width + l, 100*index*1.2 + l], [width, 100*index*1.2 + l]]
        if self.name == 'T':
            self.colour = (115, 0, 0)  # maroon
            if index == 0:
                return [[mid - l, 0], [mid - l, l], [mid - 2*l, l], [mid, l]]
            return [[width, 100*index*1.2], [width + l, 100*index*1.2], [width + 2*l, 100*index*1.2], [width + l, 100*index*1.2 + l]]
        if self.name == 'Z':
            self.colour = (127, 127, 127)  # gray
            if index == 0:
                return [[mid - l, 0], [mid, 0], [mid + l, l], [mid, l]]
            return [[width, 100*index*1.2], [width + l, 100*index*1.2], [width + l, 100*index*1.2 + l], [width + 2*l, 100*index*1.2 + l]]

    def draw(self, win, height, side=True):
        global flicker
        if Options.want_project:
            cur_block.project(height)
            for square in self.projection:
                pygame.draw.rect(win, (225, 225, 225), (square[0], square[1], self.length, self.length))
                pygame.draw.rect(win, (0, 0, 0), (square[0] + 1, square[1] + 1, self.length - 2, self.length - 2))
        for square in self.shape:
            s = pygame.Surface((self.length, self.length))
            if not side:  # so blocks in side panel don't flicker
                s.set_alpha(flicker)
            s.fill((0, 0, 0))
            win.blit(s, (square[0], square[1]))

            s = pygame.Surface((self.length - 4, self.length - 4))
            if not side:
                s.set_alpha(flicker)
            s.fill(self.colour)
            win.blit(s, (square[0] + 2, square[1] + 2))

    def move(self):
        for square in self.shape:
            square[0] += self.dir[0]
            square[1] += self.dir[1]
        for square in self.projection:
            square[0] += self.dir[0]

    def project(self, height):
        # check for collision
        # draws projection
        k = self.projection_collisions
        if ((3 in k and 2 in k) or (1 in k and 2 in k)) and self.proj_isoverlap():
            self.projection = deepcopy(self.shape)
        while 2 not in self.projection_collisions:
            for square in self.projection:
                square[1] += self.length
            self.reset_collisions(height, False)

    def reset_collisions(self, height, checkblock=True):
        if checkblock:  # normally resets collisions for both block & projection, except from project() function
            self.collisions = set([x for x in self.collide_block()] +
                                  [x for x in self.collide_ver(height)] + [x for x in self.collide_hor(width)])

        self.projection_collisions = set([x for x in self.collide_block(True)] +
                                         [x for x in self.collide_ver(height, True)])

    def collide_block(self, projecting=False):
        # check for collision with other blocks and returns dr (direction) of collision
        check = self.shape if not projecting else self.projection
        dr = set()  # use to check if no collisions in a dir then remove it from the set
        for square in check:
            for sq in Squares.square_list:
                if sq['pos'][1] - square[1] == self.length and square[0] == sq['pos'][0]:
                    dr.add(2)
                    # print('bottom')
                if sq['pos'][0] - square[0] == self.length and square[1] == sq['pos'][1]:
                    dr.add(1)
                    # print('right')
                if -sq['pos'][0] + square[0] == self.length and square[1] == sq['pos'][1]:
                    dr.add(3)
                    # print('left')
        return dr if dr else [-1]

    def collide_ver(self, height, projecting=False):
        # vertical collisions
        check = self.shape if not projecting else self.projection
        dr = set()
        for square in check:
            if square[1] >= height - self.length:  # bottom
                dr.add(2)
            if square[1] <= 0:  # top
                dr.add(0)
        return dr if dr else [-1]

    def collide_hor(self, width):
        # horizontal collisions
        dr = set()
        for square in self.shape:
            if square[0] <= 0:  # left
                dr.add(3)
            if square[0] >= width - self.length:  # right
                dr.add(1)
        return dr if dr else [-1]

    def check_hit_top(self):
        if self.isoverlap():
            return True

    def check_hit_bottom(self):
        global called, score, last, cur_block
        if 2 in self.collisions:
            if called == 0:
                last = time()
            if last_timer():
                score += 5
                if Options.want_SFX:
                    sound_lib['place'].play()
                for square in self.shape:
                    Squares.square_list.append(
                        {'pos': square,
                         'length': self.length,
                         'colour': self.colour}
                    )
                Blocks.choices.pop(0)
                cur_block = Blocks(width, no, 0)
                Blocks.get_choice()
        else:
            called = 0

    def get_origin(self):
        # determines top-right block
        x, y = 0, 9999
        for square in self.shape:
            if square[1] < y:  # finds highest points
                y = square[1]
        for square in self.shape:
            if square[1] == y and square[0] > x:  # finds right-most point from highest ones
                x = square[0]
        return [x, y]

    def rotate(self, width):
        ox, oy = self.get_origin()
        angle = pi/2
        start_shape = self.shape
        final_shape = []
        for square in self.shape:
            px, py = square[0], square[1]
            px2 = (cos(angle) * (px-ox) - sin(angle) * (py-oy)) + ox
            py2 = (sin(angle) * (px-ox) + cos(angle) * (py-oy)) + oy
            final_shape.append([round(px2), round(py2)])

        final_shape = Blocks.fix_pos(start_shape, final_shape)  # stops block from moving up or down due to rotation
        final_shape = Blocks.fix_top_overlap(final_shape)  # stops block from colliding to the top due to rotation
        final_shape = Blocks.fix_side_overlap(width, final_shape)
        self.shape = deepcopy(final_shape)
        self.retranslate(final_shape, start_shape)
        if self.shape != start_shape and Options.want_SFX:
            self.rotate_sound.play()
        self.projection = deepcopy(self.shape)

    def retranslate(self, final_shape, start_shape):
        # tries translating block by 1, 2 and 3 times its length value in left and right directions and checks for overlap
        dc = deepcopy
        if 1 in self.collide_block():
            if self.isoverlap():
                for square in self.shape:
                    square[0] -= self.length
            if self.isoverlap():
                self.shape = dc(final_shape)
                for square in self.shape:
                    square[0] -= 2 * self.length
            if self.isoverlap():
                self.shape = dc(final_shape)
                for square in self.shape:
                    square[0] -= 3 * self.length
            if self.isoverlap():
                self.shape = dc(final_shape)
            else:
                return

        if 3 in self.collide_block():
            if self.isoverlap():
                for square in self.shape:
                    square[0] += self.length
            if self.isoverlap():
                self.shape = dc(final_shape)
                for square in self.shape:
                    square[0] += 2 * self.length
            if self.isoverlap():
                self.shape = dc(final_shape)
                for square in self.shape:
                    square[0] += 3 * self.length
            if self.isoverlap():
                self.shape = dc(start_shape)
            else:
                return

    def isoverlap(self):
        for square in self.shape:
            for sq in Squares.square_list:
                if (square[0], square[1]) == (sq['pos'][0], sq['pos'][1]):
                    return True

    def proj_isoverlap(self):
        for square in self.projection:
            for sq in Squares.square_list:
                if (square[0], square[1]) == (sq['pos'][0], sq['pos'][1]):
                    return True

    @staticmethod
    def fix_pos(start_shape, final_shape):  # retranslates the position to starting one as rotation makes it move
        maxy_after, maxy_before = max([square[1] for square in final_shape]), max([square[1] for square in start_shape])
        maxx_after, maxx_before = max([square[0] for square in final_shape]), max([square[0] for square in start_shape])
        return [[square[0] + (maxx_before - maxx_after), square[1] + (maxy_before - maxy_after)] for square in final_shape]

    @staticmethod
    def fix_side_overlap(width, final_shape):
        d = min([square[0] for square in final_shape])
        if d < 0:
            return [[square[0] - d, square[1]] for square in final_shape]
        d = max([square[0] for square in final_shape])
        if d > width:
            return [[square[0] - d, square[1]] for square in final_shape]
        else:
            return final_shape

    @staticmethod
    def fix_top_overlap(final_shape):
        d = min([square[1] for square in final_shape])
        if d < 0:
            return [[square[0], square[1] - d] for square in final_shape]
        else:
            return final_shape

    def skip(self):
        global cur_block, skip_count
        if skip_count > 0:
            Blocks.choices.pop(0)
            cur_block = Blocks(width, no, 0)
            Blocks.get_choice()
            skip_count -= 1

class Buttons:
    def __init__(self, text, lenx, leny, posx, posy, func, args=None, colour1=(0, 0, 255), colour2=(255, 0, 0)):
        self.click = sound_lib['click']
        self.colour1 = colour1
        self.colour2 = colour2
        self.show_colour2 = False
        self.lenx = lenx
        self.leny = leny
        self.posx = posx
        self.posy = posy
        self.text = text
        self.func = func
        self.args = args

    def draw(self, win, font):
        if not self.show_colour2:
            pygame.draw.rect(win, (0, 0, 0), (self.posx, self.posy, self.lenx, self.leny))  # posx takes into acc lenx
            pygame.draw.rect(win, self.colour1, (self.posx + 2, self.posy + 2, self.lenx - 4, self.leny - 4))
        else:
            pygame.draw.rect(win, (0, 0, 0), (self.posx, self.posy, self.lenx, self.leny))
            pygame.draw.rect(win, self.colour2, (self.posx + 2, self.posy + 2, self.lenx - 4, self.leny - 4))
        text = font.render(self.text, 1, (0, 0, 0))
        win.blit(text, (self.posx + (self.lenx - text.get_width()) // 2, self.posy + (self.leny - text.get_height()) // 2))

    def isover(self):
        pos = pygame.mouse.get_pos()
        if self.posx < pos[0] < (self.posx + self.lenx) and self.posy < pos[1] < (self.posy + self.leny):
            self.show_colour2 = True
            return True
        else:
            self.show_colour2 = False
            return False

    def isclicked(self):
        if self.isover():
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if Options.want_SFX:
                        self.click.play()
                    try:
                        self.func(*self.args)
                    except TypeError:
                        self.func()

class Options:
    want_project = True
    want_SFX = True
    want_Music = True
    want_pause = False

    @staticmethod
    def instructions(win, font, h):
        instruction = """ Welcome to the classic Tetris! It is a fun and simple game where you try to arrange the blocks and fill up each line from bottom up.Every correctly placed block earns you 5 points and a correctly filled line disappears earns you 10. But if the blocks reach the top of the page, you lose. Survive as long as you can. """
        text = TextWrapper()
        text = text.wrap(instruction)
        for line in text:
            show = font.render(line, 1, (0, 225, 0))
            win.blit(show, (50, h*(text.index(line) + 1.5)))

    @classmethod
    def pause(cls):
        cls.want_pause = not cls.want_pause

    @classmethod
    def project(cls):
        cls.want_project = not cls.want_project

    @classmethod
    def music(cls):
        cls.want_Music = not cls.want_Music
        if not cls.want_Music:
            pygame.mixer.music.stop()
        else:
            pygame.mixer.music.play(-1)

    @staticmethod
    def inc_mvol():
        cur_vol = pygame.mixer.music.get_volume()
        if cur_vol < 1:
            pygame.mixer_music.set_volume(cur_vol+0.1)

    @staticmethod
    def dec_mvol():
        cur_vol = pygame.mixer.music.get_volume()
        if cur_vol > 0:
            pygame.mixer_music.set_volume(cur_vol - 0.1)

    @staticmethod
    def inc_svol():
        cur_vol = sound_lib['click'].get_volume()  # all have the same volume
        if cur_vol < 1:
            sound_lib['delete'].set_volume(cur_vol + 0.1)
            sound_lib['click'] .set_volume(cur_vol + 0.1)
            sound_lib['rotate'].set_volume(cur_vol + 0.1)
            sound_lib['place'] .set_volume(cur_vol + 0.1)

    @staticmethod
    def dec_svol():
        cur_vol = sound_lib['click'].get_volume()
        if cur_vol > 0:
            sound_lib['delete'].set_volume(cur_vol - 0.1)
            sound_lib['click'] .set_volume(cur_vol - 0.1)
            sound_lib['rotate'].set_volume(cur_vol - 0.1)
            sound_lib['place'] .set_volume(cur_vol - 0.1)

    @classmethod
    def SFX(cls):
        cls.want_SFX = not cls.want_SFX

def create_grid(win, width, height, no):
    for x in range(no + 1):
        pygame.draw.line(win, (225,225,225), (x*cur_block.length, 0), (x*cur_block.length, height))
    for y in range(no + 1):
        pygame.draw.line(win, (225,225,225), (0, y*cur_block.length), (width, y*cur_block.length))

def down_timer(cur_block):  # moves block down every x seconds
    global start
    now = time()
    if now - start >= 2:
        if 2 not in cur_block.collisions:
            cur_block.dir = (0, cur_block.length)
            cur_block.move()
            cur_block.dir = (0, 0)
        start = time()
        return True
    return False

def last_timer():  # allows for final repositioning before next block appears
    global last, called
    called = 1
    now = time()
    flick(now-last)
    if now - last >= 1:
        last = time()
        called = 0
        return True

def retry():
    global called, flicker, score, last, start, cur_block, end
    called = 0
    flicker = 255
    score = 0
    last = time()
    start = time()

    end = False
    Options.want_pause = False
    cur_block = Blocks(width, no, 0)
    Squares.square_list = []

def get_name():
    global win
    name = ''
    prompt = 'Please write your name: '
    iterate = True
    font = pygame.font.SysFont("comicsans", 30, True)
    while iterate:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                break
            if event.type == pygame.KEYDOWN:
                if pygame.key.name(event.key) == 'backspace':
                    name = name[:-1] if len(name) > 1 else '' # doesn't work because the removed character isn't blitted over by bg
                    print('name: ', name)
            elif event.type == pygame.KEYUP:
                if pygame.key.name(event.key) == 'return':
                    iterate = False
                    break
                elif 97 <= event.key <= 122:
                    name += chr(event.key)

        pygame.draw.rect(win, (240, 0, 255), (1.3 * (win_width - width), height - 130, width, 30)) # blits a pink rectangle over the input spot to blit over erased characters
        n = font.render(name, 1, (0, 0, 0))
        win.blit(n, (1.3 * (win_width - width), height - 130))
        i = font.render(prompt, 1, (0, 0, 0))
        win.blit(i, (1.3 * (win_width - width) - i.get_width(), height - 130))
        pygame.display.update()
    return name

def get_index(old_table):
    global score
    sc = score
    scores = []
    for line in old_table:
        scores.append(line.split(sep=':')[1][1:-1])
    for s in scores:
        if int(s) < sc:
            print(scores.index(s))
            return scores.index(s)
    return -1

def save():
    name = get_name()
    with open("saved scores.txt", "r") as s:
        table = s.readlines()
    with open("saved scores.txt", "w") as s:
        ind = get_index(table)
        if ind == -1:
            s.writelines(table)
            return
        else:
            table[ind] = f'{name}: {str(score)}\n'
            s.writelines(table)

def load_buttons(win, win_width, width, height, game=True, pause=False, end=False):

    if pause: mvol_text, svol_text = load_text(win, width, game=False, pause=True)
    else: load_text(win, width, game=game, pause=pause, end=end)

    font = pygame.font.SysFont("comicsans", 30, True)

    quit = Buttons('Quit', 0.85 * (win_width - width), 0.1 * height, width + 20, height - 100, pygame.quit)
    quit.isclicked()
    quit.draw(win, font)

    if not end:
        toggle_pause_text = 'Pause' if game else 'Resume' if pause else 'Settings'
        toggle_pause = Buttons(toggle_pause_text, 0.85 * (win_width - width), 0.1 * height, width + 20, height - 200, Options.pause)
        toggle_pause.isclicked()
        toggle_pause.draw(win, font)

    if game:
        skipper = Buttons(f'Skips left: {skip_count}', 0.85 * (win_width - width), 0.1 * height, width + 20, height - 300, cur_block.skip)
        skipper.isclicked()
        skipper.draw(win, font)

    if pause or end:
        restart = Buttons('Restart', 0.85 * (win_width - width), 0.1 * height, 0.1 * width, height - 100, retry)
        restart.isclicked()
        restart.draw(win, font)

    if pause:
        toggle_projection_text = 'Projection ON' if Options.want_project else 'Projection OFF'
        toggle_projection = Buttons(toggle_projection_text, 0.85 * (win_width - width), 0.1 * height, 0.55 * width, height - 100, Options.project)
        toggle_projection.isclicked()
        toggle_projection.draw(win, font)

        toggle_music_text = 'Music ON' if Options.want_Music else 'Music OFF'
        toggle_music = Buttons(toggle_music_text, 0.85 * (win_width - width), 0.1 * height, 0.1 * width, height - 200, Options.music)
        toggle_music.isclicked()
        toggle_music.draw(win, font)

        inc_mvol = Buttons('+', 0.2 * (win_width - width), 0.03 * height, 0.95 * width + mvol_text.get_width() + 5, height - 300, Options.inc_mvol)
        inc_mvol.isclicked()
        inc_mvol.draw(win, font)

        dec_mvol = Buttons('-', 0.2 * (win_width - width), 0.03 * height, 0.95 * width + mvol_text.get_width() + 55, height - 300, Options.dec_mvol)
        dec_mvol.isclicked()
        dec_mvol.draw(win, font)

        inc_svol = Buttons('+', 0.2 * (win_width - width), 0.03 * height, 0.95 * width + svol_text.get_width() + 5, height - 250, Options.inc_svol)
        inc_svol.isclicked()
        inc_svol.draw(win, font)

        dec_svol = Buttons('-', 0.2 * (win_width - width), 0.03 * height, 0.95 * width + svol_text.get_width() + 55, height - 250, Options.dec_svol)
        dec_svol.isclicked()
        dec_svol.draw(win, font)

        toggle_SFX_text = 'SFX ON' if Options.want_SFX else 'SFX OFF'
        toggle_SFX = Buttons(toggle_SFX_text, 0.85 * (win_width - width), 0.1 * height, 0.55 * width, height - 200, Options.SFX)
        toggle_SFX.isclicked()
        toggle_SFX.draw(win, font)

    elif end:
        restart = Buttons('Restart', 0.85 * (win_width - width), 0.1 * height, 0.1 * width, height - 100, retry)
        restart.isclicked()
        restart.draw(win, font)

        saver = Buttons('Save score', 0.85 * (win_width - width), 0.1 * height, 0.55 * width, height - 100, save)
        saver.isclicked()
        saver.draw(win, font)

def load_text(win, width, game=True, pause=False, end=False):

    font = pygame.font.SysFont("comicsans", 30, True)

    if not end:
        score_text = font.render(f'Score: {score}', 1, (0, 0, 0))
        win.blit(score_text, (width + 20, 30 + score_text.get_height() // 2))

    if game:
        next_text = font.render('Next: ', 1, (0, 0, 0))
        win.blit(next_text, (width + 20, 30 + next_text.get_height() + score_text.get_height()))
    if pause:
        mvol_text = font.render(f'Music vol: {round(pygame.mixer.music.get_volume() * 10)}', 1, (0, 0, 0))
        win.blit(mvol_text, (0.95 * width, height - 300))

        svol_text = font.render(f'SFX vol: {round(sound_lib["click"].get_volume() * 10)}', 1, (0, 0, 0))
        win.blit(svol_text, (0.95 * width, height - 250))

        Options.instructions(win, font, 60)

        font = pygame.font.SysFont("comicsans", 60, True)
        pause_text = font.render(f'Paused', 1, (200, 0, 0))
        win.blit(pause_text, (width // 2, pause_text.get_height() // 2))

        return (mvol_text, svol_text)

    if end:
        with open("saved scores.txt", "r") as s:  # prints saved high scores
            high_score_text = s.readlines()
            text = [line.split(sep=':') for line in high_score_text]
            for i in range(len(text)):
                name = font.render(text[i][0], 1, (0, 0, 0))
                win.blit(name,(0.3 * width, 30 + 0.25 * height + 30 * i))

                scores = font.render(text[i][1][:-1], 1, (0, 0, 0))
                win.blit(scores, (0.9 * width, 30 + 0.25 * height + 30 * i))
        font = pygame.font.SysFont("comicsans", 50, True)
        lost_text = font.render(f'You lost with {score} points', 1, (0, 0, 0))
        win.blit(lost_text, (0.4 * width, 30 + lost_text.get_height()))

        name_text = font.render('Name', 1, (0, 0, 0))
        win.blit(name_text, (0.3*width, 60 + lost_text.get_height() + name_text.get_height()))

        scores_text = font.render('Score', 1, (0, 0, 0))
        win.blit(scores_text, (0.9*width, 60 + lost_text.get_height() + name_text.get_height()))

def gamewindow(win_width, width, height, no, win):
    global cur_block
    create_grid(win, width, height, no)
    load_buttons(win, win_width, width, height)

    down_timer(cur_block)
    cur_block.check_hit_bottom()

    if cur_block.collisions == {-1}:
        flick(0, True)

    Squares.draw(win)
    cur_block.draw(win, height, side=False)

    next1 = Blocks(width, no, 1)  # side panel
    next1.draw(win, height, side=True)
    next2 = Blocks(width, no, 2)
    next2.draw(win, height, side=True)

def flick(diff, moved=False):  # makes block flicker at the bottom
    global flicker
    if moved:
        flicker = 255
        return
    if diff <= 0.5:
        flicker = 255-(diff*510)
    elif diff > 0.5:
        flicker = diff*510

def set_keyboard_dirs(cur_block, width, height):
    global move_timer, keys, rotate_timer
    cur_block.reset_collisions(height)
    cur_block.dir = (0, 0)
    keys = pygame.key.get_pressed()
    if (keys[pygame.K_UP] or keys[pygame.K_w]) and rotate_timer == 0:
        cur_block.rotate(width)
        rotate_timer = 20
    elif keys[pygame.K_SPACE]:
        cur_block.shape = deepcopy(cur_block.projection)
    elif (keys[pygame.K_DOWN] or keys[pygame.K_s]) and 2 not in cur_block.collisions:
        cur_block.dir = (0, cur_block.length)
    elif (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and 1 not in cur_block.collisions:
        cur_block.dir = (cur_block.length, 0)
    elif (keys[pygame.K_LEFT] or keys[pygame.K_a]) and 3 not in cur_block.collisions:
        cur_block.dir = (-cur_block.length, 0)
    if cur_block.dir != (0, 0) and move_timer == 0:
        cur_block.move()
        move_timer = 10

# highscores dict and calling for the first run, afterwards its saves
# high_scores = {'The supreme overlord Vijay': 1312982,
#                'BTEC guy1': 1294,
#                'BTEC guy2': 1153,
#                'BTEC guy3': 983,
#                'BTEC guy4': 812,
#                "Servant 1": 714,
#                "Servant 2": 629,
#                "Servant 3": 528,
#                "Servant 4": 486
#     }
# scores = [f'{name}: {scores}\n' for name, scores in high_scores.items()]
# with open("saved scores.txt", "w") as s:
#     s.writelines(scores)
sound_lib = {'delete': pygame.mixer.Sound('deleting.wav'),
             'click': pygame.mixer.Sound('mouse-click.wav'),
             'rotate': pygame.mixer.Sound('rotate.wav'),
             'place': pygame.mixer.Sound('placing.wav')}
pygame.mixer.music.load('Tetris theme.wav')
pygame.mixer.music.play(-1)

win_width = 900  # window size, some scaling issues for some combos of win_width, width
width = round(0.7*win_width)  # game screen size
win_height, height = width, width
win = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("Tetris")

no = 15  # no of squares
called = 0
flicker = 255
score = 0
skip_count = 5
end = False
move_timer = 0
rotate_timer = 0
start = time()
last = time()

running = True

Blocks.get_choice()
cur_block = Blocks(width, no, 0)

grid_squares = [cur_block.length*i for i in range(no)]

# main loop
while running:
    try:
        win.fill((240, 0, 255))
        events = pygame.event.get()

        if Options.want_pause:
            load_buttons(win, win_width, width, height, game=False, pause=True)
        elif end:
            load_buttons(win, win_width, width, height, game=False, pause=False, end=True)
        else:
            gamewindow(win_width, width, height, no, win)
            set_keyboard_dirs(cur_block, width, height)

            if cur_block.check_hit_top():
                end = True

            try:
                lines = reversed(range(min([square['pos'][1] for square in Squares.square_list]), height, cur_block.length))
                for line_no in reversed(range(min([square['pos'][1] for square in Squares.square_list]), height)):
                    line_sq = Squares.check_line(line_no, no)  # list of squares or None
                    if line_sq:
                        score += 50
                        Squares.del_square(line_sq, line_no)
            except ValueError:
                pass
            if move_timer > 0:
                move_timer -= 1
            if rotate_timer > 0:
                rotate_timer -= 1

        pygame.display.update()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
                break
    except:
        print(sys.exc_info())
        print(sys.exc_info()[0])
        input("Press any key to continue")