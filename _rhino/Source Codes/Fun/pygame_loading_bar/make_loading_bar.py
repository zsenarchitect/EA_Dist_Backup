import sys
sys.path.append("..\lib")
import EnneadTab
"""this thing works, but too slow to initate as exe to be usful.
Need to do next version similar to standby speaker.
"""



# Imports
import pygame, sys, threading, time, json, os

pygame.init()

# Screen and font
TOTAL_W = 900
TOTAL_H = 400
screen = pygame.display.set_mode((TOTAL_W, TOTAL_H))
pygame.display.set_caption("EneadTab is Loading...")

FONT = pygame.font.SysFont("Roboto", 50)



# Clock
CLOCK = pygame.time.Clock()

# Work
WORK = 8000000# if number too large, the progress bar will not show

# Loading BG
path = r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\Fun\pygame_loading_bar\Loading Bar Background.png'
try:
	LOADING_BG = pygame.image.load("Loading Bar Background.png")
except:
	LOADING_BG = pygame.image.load(path)	
LOADING_BG_RECT = LOADING_BG.get_rect(center=(TOTAL_W/2, TOTAL_H/2 + 50))

# Loading Bar and variables
path = r'L:\4b_Applied Computing\03_Rhino\12_EnneadTab for Rhino\Source Codes\Fun\pygame_loading_bar\Loading Bar.png'
try:
	loading_bar = pygame.image.load("Loading Bar.png")
except:
	loading_bar = pygame.image.load(path)
loading_bar_rect = loading_bar.get_rect(midleft=(TOTAL_W/2-360, TOTAL_H/2 + 50))
loading_finished = False
loading_progress = 0
loading_bar_width = 8




def read_json_as_dict(filepath):
    
    # reads it back
    with open(filepath,"r") as f:
      dict = json.load(f)
    return dict




dump_folder =  "{}\Documents\EnneadTab Settings\Local Copy Dump".format(os.environ["USERPROFILE"])
text_source_file = "EA_LOADING_SCREEN_TEXT.json"
if text_source_file in os.listdir(dump_folder):
	file = "{}\{}".format(dump_folder, text_source_file)
	data = read_json_as_dict(file)
	text_source = data["text"]
	TIME_SPAN = data["time"]
else:
	text_source = "EnneadTab is Loading!"
	TIME_SPAN = 2
main_text = FONT.render(text_source, True, "white")
main_text_rect = main_text.get_rect(center=(TOTAL_W/2, TOTAL_H/2 - 100))

def doWork():
	# Do some math WORK amount times
	global loading_finished, loading_progress

	begin_time = time.time()
	i = 0
	while i < WORK:
		math_equation = 523687 / 789456 * 89456 * 3203250054608540
		loading_progress = i 
		#print (i+1)
		time_span = time.time() - begin_time
		#print (time_span)
		if time_span  > TIME_SPAN:
			i +=10
			continue
		i += 1
		
		

	loading_finished = True

# Finished text
finished = FONT.render("Done!", True, "white")
finished_rect = finished.get_rect(center=(TOTAL_W/2, TOTAL_H/2))

# Thread
threading.Thread(target=doWork).start()

# Game loop
while True:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			pygame.quit()
			sys.exit()

	screen.fill("#0d0e2e") #orioginal blue
	#screen.fill("#0d2e22")# new greeen
	

	if not loading_finished:
		loading_bar_width = loading_progress / WORK * 720
		#print (loading_progress / WORK)

		loading_bar = pygame.transform.scale(loading_bar, (int(loading_bar_width), 150))
		loading_bar_rect = loading_bar.get_rect(midleft=(TOTAL_W/2-360, TOTAL_H/2 + 50))

		screen.blit(LOADING_BG, LOADING_BG_RECT)
		screen.blit(loading_bar, loading_bar_rect)
		screen.blit(main_text, main_text_rect)
	else:
		screen.blit(finished, finished_rect)
		pygame.display.update()
		#pygame.time.wait(1500)
		pygame.quit()
		sys.exit()

	# loading_bar_width = loading_progress / WORK * 720

	# loading_bar = pygame.transform.scale(loading_bar, (int(loading_bar_width), 150))
	# loading_bar_rect = loading_bar.get_rect(midleft=(280, 360))

	# screen.blit(LOADING_BG, LOADING_BG_RECT)
	# screen.blit(loading_bar, loading_bar_rect)

	pygame.display.update()
	CLOCK.tick(60)