import pygame
import neat
import time
import os
import random
pygame.font.init()

import keyboard

WIN_WIDTH = 286
WIN_HEIGHT = 500

BIRD_IMGS = [pygame.image.load(os.path.join("imgs", "bird1.png")), pygame.image.load(os.path.join("imgs", "bird2.png")), pygame.image.load(os.path.join("imgs", "bird3.png"))]
PIPE_IMG = pygame.image.load(os.path.join("imgs", "pipe.png"))
BASE_IMG = pygame.image.load(os.path.join("imgs", "base.png"))
BG_IMG = pygame.image.load(os.path.join("imgs", "bg.png"))

STAT_FONT = pygame.font.SysFont("comicsans", 50)

class Bird:
	IMGS = BIRD_IMGS
	MAX_ROTATION = 25
	ROT_VEL = 20
	ANIMATION_TIME = 3

	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.tilt = 0
		self.tick_count = 0
		self.vel = 0
		self.height = self.y
		self.img_count = 0
		self.img = self.IMGS[0]

	def jump(self):
		#self.vel = -10.5 #pogledati sliku koncept2
		self.vel = -5.5
		self.tick_count = 0
		self.height = self.y

	def move(self):
		self.tick_count += 1

		d = self.vel*self.tick_count + 1.5*self.tick_count**2
		
		if d >= 12:
			d = 12

		if d < 0:
			d -= 2

		self.y = self.y + d

		if d < 0 or self.y < self.height + 50:
			if self.tilt < self.MAX_ROTATION:
				self.tilt = self.MAX_ROTATION
		else:
			if self.tilt > -90:
				self.tilt -= self.ROT_VEL

	def draw(self, win):
		self.img_count += 1

		#mahanje krila ptice
		if self.img_count < self.ANIMATION_TIME:
			self.img = self.IMGS[0]
		elif self.img_count < self.ANIMATION_TIME*2:
			self.img = self.IMGS[1]
		elif self.img_count < self.ANIMATION_TIME*3:
			self.img = self.IMGS[2]
		elif self.img_count < self.ANIMATION_TIME*4:
			self.img = self.IMGS[1]
		elif self.img_count == self.ANIMATION_TIME*4 + 1:
			self.img = self.IMGS[0]
			self.img_count = 0

		#proveravamo da ne mase krilima kada pada
		if self.tilt <= -80:
			self.img = self.IMGS[1]
			self.img_count = self.ANIMATION_TIME*2 #da bi sledece bilo IMGS[2], da zamahne krilima kad skoci

		#rotiranje slike oko centra svoje ose sa pygame
		rotated_image = pygame.transform.rotate(self.img, self.tilt) #ovo rotira sliku oko top left strane
		new_rect = rotated_image.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center) #ovo rotira sliku oko centra
		win.blit(rotated_image, new_rect.topleft) #i ne mora .topleft
		#win.blit(rotated_image, (self.x, self.y))

	def get_mask(self):
		return pygame.mask.from_surface(self.img)


class Pipe:
	GAP = 100
	VEL = 4

	def __init__(self, x):
		self.x = x
		self.height = 0

		self.top = 0
		self.bottom = 0
		self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)
		self.PIPE_BOTTOM = PIPE_IMG

		self.passed = False
		self.set_height()

	def set_height(self):
		self.height = random.randrange(50, 300)
		self.top = self.height - self.PIPE_TOP.get_height()
		self.bottom = self.height + self.GAP

	def move(self):
		self.x -= self.VEL #pomera se samo po x koordinati

	def draw(self, win):
		win.blit(self.PIPE_TOP, (self.x, self.top)) #crtamo gornju cev
		win.blit(self.PIPE_BOTTOM, (self.x, self.bottom)) #crtamo donju cev

	def collide(self, bird):
		bird_mask = bird.get_mask() #maska za ticu
		top_mask = pygame.mask.from_surface(self.PIPE_TOP)
		bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)

		top_offset = (self.x - bird.x, self.top - round(bird.y)) #koliko daleko su dva top left ugla udaljena, round da nemamo decimalnih brojeva
		bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

		b_point = bird_mask.overlap(bottom_mask, bottom_offset) #proveravamo da li se maske sudaraju; point of collision...point of collision izmedju bird_mask i bottom_mask (pipe) koristeci bottom_ofset...f-ja vraca None ako se ne sudaraju maske
		t_point = bird_mask.overlap(top_mask, top_offset)

		if t_point or b_point: #provera da li ove tacke uopste postoje, ako nisu None onda
			return True #znaci da smo se sudarili sa drugim objektom
		return False #inace vrati false


class Base:
	VEL = 4 #ista brzina kao i za cev
	WIDTH = BASE_IMG.get_width()
	IMG = BASE_IMG

	def __init__(self, y):
		self.y = y
		self.x1 = 0
		self.x2 = self.WIDTH

	def move(self):
		self.x1 -= self.VEL
		self.x2 -= self.VEL

		if self.x1 + self.WIDTH < 0:
			self.x1 = self.x2 + self.WIDTH

		if self.x2 + self.WIDTH < 0:
			self.x2 = self.x1 + self.WIDTH

	def draw(self, win):
		win.blit(self.IMG, (self.x1, self.y))
		win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, bird, pipes, base, score):
	win.blit(BG_IMG, (0,0)) #blit means draw, (0,0) je na topleft poziciji ekrana

	for pipe in pipes:		#prvo crtamo pipes pa tek onda bazu, da ne bi cevi bile preko baze
		pipe.draw(win)

	text = STAT_FONT.render("Score: " + str(score), 1, (0,0,0)) #
	win.blit(text, (WIN_WIDTH - text.get_width(), 0)) #iscrtaj text sa zadatim x i y koordinatama

	base.draw(win)

	bird.draw(win) #prosledjujemo metodi win na kome ce da iscrta sve
	pygame.display.update() #updates display


def main():
	bird = Bird(90,200) #kreirali objekat ticu, zadali koordinate gde ce da se stvori na ekranu

	base = Base(WIN_HEIGHT - 50)

	pipes = [Pipe(600)] #razmak izmedju cevi je 600 jedinica

	win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT)) #kreirali objekat windowsa gde ce biti igrica, u sustini ekran na kom se igra igra

	clock = pygame.time.Clock() #ovo implementiramo da tica ne bi pala odmah kad se pokrene igra, set the frame rate of the loop

	score = 0

	gotovo = False

	prvi_key_press = False

	run = True
	while run:
		clock.tick(30) #najvise 30 tikova u sekundi, padace sporije
		for event in pygame.event.get(): #kad god se nesto desi, npr korisnik klikne misem
			if event.type == pygame.QUIT: #ako pritisnemo crveni iks u gornjem desnom uglu
				run = False #izlazi iz petlje

		if keyboard.is_pressed('u'):
			prvi_key_press = True
			bird.jump()

		if prvi_key_press:
			bird.move()

		add_pipe = False

		rem = [] #lista za brisanje cevi remove
		for pipe in pipes:
			if pipe.collide(bird):
				#pass
				gotovo = True
				run = False

			if pipe.x + pipe.PIPE_TOP.get_width() < 0: #ako je cev skroz izasla sa ekrana
				rem.append(pipe)

			if not pipe.passed and pipe.x < bird.x:
				pipe.passed = True
				add_pipe = True

			pipe.move()

		if add_pipe:
			score += 1
			pipes.append(Pipe(300))

		for r in rem:
			pipes.remove(r)

		if bird.y + bird.img.get_height() >= WIN_HEIGHT - 50: #zapamti da y na dole raste
			#pass
			gotovo = True
			run = False

		if keyboard.is_pressed('u'):
			bird.jump()


		base.move()
		draw_window(win, bird, pipes, base, score) #pozivamo metodu


	while gotovo:
		gameover = STAT_FONT.render("Restar? (y/n)!", 1, (255,255,255))
		rect = gameover.get_rect()
		rect.center = win.get_rect().center
		win.blit(BG_IMG, (0,0))
		win.blit(gameover, rect)

		rez = STAT_FONT.render("Score: " + str(score), 1, (0,0,0))
		win.blit(rez, (35, 200))

		pygame.display.update()
		for event in pygame.event.get(): #kad god se nesto desi, npr korisnik klikne misem
			if event.type == pygame.QUIT: #ako pritisnemo crveni iks u gornjem desnom uglu
				run = False #izlazi iz petlje
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_y and gotovo:
					gotovo = False
					main()
				elif event.key == pygame.K_n and gotovo:
					gotovo = False
					run = False

	pygame.quit() #izlazi iz pygame
	quit() #izlazi iz programa

main()

"""



ghk
ghkg
"""