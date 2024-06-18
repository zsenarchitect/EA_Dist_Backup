import sys
sys.path.append("..\lib")
import EnneadTab
"""
tryied this but cannot use pygame module directly in rhino environment
import sys
import EnneadTab
sys.path.append(EnneadTab.ENVIRONMENT.DEPENDENCY_FOLDER_LEGACY)

from pygame import camera
"""
import pygame
import button
import traceback
import os
import math

def rotate_img_around_center(image, rect, angle):
    """Rotate the image while keeping its center."""
    # Rotate the original image without modifying it.
    new_image = pygame.transform.rotate(image, angle)
    # Get a new rect with the center of the old rect.
    rect = new_image.get_rect(center=rect.center)
    return new_image, rect


def get_pointer_angle(pt_x, pt_y):
    """get the angle of a line[current mouse position to a given pt] to X axis"""
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if mouse_x == pt_x:
      return 90 + 180 * (mouse_y > pt_y)
    angle = math.atan(-float(mouse_y - pt_y) / float(mouse_x - pt_x))* 180 / math.pi
    angle += 180 * (mouse_x < pt_x)# force extra rotate
    return angle

@EnneadTab.ERROR_HANDLE.try_catch_error
def main():
    script_dir = os.path.abspath( os.path.dirname( __file__ ) )
    print("A GUI designed by Sen Zhang for Ennead Architect.")
    # print ("%%%%%%%%%%%%%%%%%%%%%")
    # print (script_dir)
    pygame.init()

    #create game window
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("EnneadTab Main Menu")

    #game variables
    game_paused = False
    menu_state = "main"

    #define fonts
    font = pygame.font.SysFont("arialblack", 20)

    #define colours
    TEXT_COL = (255, 255, 255)

    # logo
    EA_logo = pygame.image.load("{}\\images\\Ennead_Architects_Logo.png".format(script_dir)).convert_alpha()
    target_img_size = (100, 100)
    EA_logo = pygame.transform.scale(EA_logo, target_img_size)
    original_logo = EA_logo
    logo_rect = EA_logo.get_rect(center=(100, SCREEN_HEIGHT - 100))
    angle = 0

    # Clock
    clock = pygame.time.Clock()
    FPS = 60

    #load button images
    resume_img = pygame.image.load("{}\\images\\button_resume.png".format(script_dir)).convert_alpha()
    options_img = pygame.image.load("{}\\images\\button_options.png".format(script_dir)).convert_alpha()
    quit_img = pygame.image.load("{}\\images\\button_quit.png".format(script_dir)).convert_alpha()
    video_img = pygame.image.load('{}\\images\\button_video.png'.format(script_dir)).convert_alpha()
    audio_img = pygame.image.load('{}\\images\\button_audio.png'.format(script_dir)).convert_alpha()
    keys_img = pygame.image.load('{}\\images\\button_keys.png'.format(script_dir)).convert_alpha()
    back_img = pygame.image.load('{}\\images\\button_back.png'.format(script_dir)).convert_alpha()

    #create button instances
    resume_button = button.Button(304, 125, resume_img, 1)
    options_button = button.Button(297, 250, options_img, 1)
    quit_button = button.Button(336, 375, quit_img, 1)
    video_button = button.Button(226, 75, video_img, 1)
    audio_button = button.Button(225, 200, audio_img, 1)
    keys_button = button.Button(246, 325, keys_img, 1)
    back_button = button.Button(332, 450, back_img, 1)

    def draw_text(text, font, text_col, x, y):
        img = font.render(text, True, text_col)
        screen.blit(img, (x, y))

    #game loop
    run = True


    while run:

        screen.fill((52, 78, 91))


        """
        logo_rotate_index_now = int(pygame.time.get_ticks() / 1000)
        if logo_rotate_index_now != logo_rotate_index_record:
          logo_rotate_index_record = logo_rotate_index_now
          #new_rect = rotated_image.get_rect(center = image.get_rect(center = (x, y)).center)
          original_center = EA_logo.get_rect().center

          EA_logo = pygame.transform.rotate(EA_logo, 10)
          logo_rect = EA_logo.get_rect(center = original_center)
        """
        if game_paused == False:# in main window
          #print "in main window"
          angle += 0.3# this is to slowyg rotate
        else: # game_paused == True:
          if menu_state != "options":
              #print "in first pause window"
              angle = get_pointer_angle(*logo_rect.center)# this is to keep it facing mouse
          else:
              #print "in other window"
              angle -= 10

        EA_logo, logo_rect = rotate_img_around_center(original_logo, logo_rect, angle)
        screen.blit(EA_logo, logo_rect)

        #check if game is paused
        if game_paused == True:
            #check menu state
            if menu_state == "main":
                draw_text("The logo follow your mouse position", font, TEXT_COL, 50, 50)



                #draw pause screen buttons
                if resume_button.draw(screen):
                    game_paused = False
                if options_button.draw(screen):
                    menu_state = "options"
                if quit_button.draw(screen):
                    run = False
            #check if the options menu is open
            if menu_state == "options":
                draw_text("The logo quickly rotate clockwise. Only 'back' works at the moment.", font, TEXT_COL, 50, 30)


                #draw the different options buttons
                if video_button.draw(screen):
                    print("Video Settings")
                if audio_button.draw(screen):
                    print("Audio Settings")
                if keys_button.draw(screen):
                    print("Change Key Bindings")
                if back_button.draw(screen):
                    menu_state = "main"
        else:
            draw_text("Press SPACE to pause and show menu.", font, TEXT_COL, 50, 50)
            draw_text("The logo slowly rotate counter-clockwise. \nTry other menu..", font, TEXT_COL, 50, 70)

        #event handler
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_paused = True
            if event.type == pygame.QUIT:
                run = False

        clock.tick(FPS)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":

    main()


