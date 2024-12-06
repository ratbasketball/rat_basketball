import os
os.environ["SDL_VIDEO_ALLOW_SCREENSAVER"] = "1"
os.environ["SDL_JOYSTICK_ALLOW_BACKGROUND_EVENTS"] = "1"
os.environ["SDL_VIDEO_X11_NET_WM_BYPASS_COMPOSITOR"] = "0"
import pygame
from pygame.locals import *
import math
import sys
import pygame_menu
from pygame_menu import themes
import RPi.GPIO as GPIO
import pigpio


#Recall: I did need to go into the controls.py file and edit it to function with my NES controllers
# I need to edit it to the following: 

# Joy pad
# JOY_AXIS_X = 0
# JOY_AXIS_Y = 1
# JOY_BUTTON_BACK = 2
# JOY_BUTTON_SELECT = 1
# JOY_DEADZONE = 0.5
# JOY_DELAY = 300  # ms
# JOY_DOWN = (0, -1)
# JOY_LEFT = (-1, 0)
# JOY_REPEAT = 100  # ms
# JOY_RIGHT = (1, 0)
# JOY_UP = (0, 1)

# initialize pygame stuff
pygame.init()
pygame.font.init()
pygame.joystick.init()

# Initialize some variables and stuff
joysticks = {}
gameTimerMinutes = 0 # unless altered in the start menu
player1Score = 0
player2Score = 0

# setup the game, this code will run only once
pygame.display.set_caption("Rat Basketball")  # see: https://www.pygame.org/docs/ref/display.html
# Note: use full screen below whenever possible, as the font
# will render without exiting the screen.  If necessary, edit font size
# screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN,display=0) 
screen = pygame.display.set_mode((900, 700), pygame.RESIZABLE)
X,Y = screen.get_width(), screen.get_height()
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)
background = GRAY 
screen.fill(background)

# setup score board text stuff
player1Name = 'Player 1'
player2Name = 'Player 2'
sysfont = pygame.font.get_default_font()
font = pygame.font.SysFont(None, 48)

playerNameFont = pygame.font.SysFont(None, 250) # may need to make this dynamically updatable
playerScoreFont = pygame.font.SysFont(None, 550) # may need to make this dynamically updatable
timerFont = pygame.font.SysFont(None, 300) # may need to make this dynamically updatable

##############
###  GPIO  ###
##############

pi = pigpio.pi('soft', 8888)
# Time Constants
BUTTON_PRESS_DELAY = 0.3 # Delay between each button press
STEADY_SIGNAL_MICROSECONDS = 300000 # Microseconds needed to trigger a steady electrical signal (avoid false triggers)
lightOnTimeSeconds = 1
lightOnTimeMilliseconds = lightOnTimeSeconds * 1000
player1LightTimeLock = 0
player2LightTimeLock = 0

# GPIO Constants
GPIO_INPUT_P1BASKET = 7 # IO4 on breakout hat CE1 GPIO23 Player 1 - Button A --> Was 12 (GPIO18) before
GPIO_OUTPUT_P1LIGHT = 10 #GPIO 15  UART0 RX
GPIO_INPUT_P2BASKET = 29  # GPIO 05 # GPIO24 Player 1 - Button B #GPIO_INPUT_P2BASKET = 18 # GPIO24 Player 1 - Button B
GPIO_OUTPUT_P2LIGHT = 32 #GPIO 12

# GPIO inputs & outputs configuration
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(GPIO_OUTPUT_P1LIGHT, GPIO.OUT)
GPIO.setup(GPIO_OUTPUT_P2LIGHT, GPIO.OUT)
GPIO.setup(GPIO_INPUT_P1BASKET, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(GPIO_INPUT_P2BASKET, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# The below sets up the basket toggle which makes it so that 
# after the basket is activated it will not activate again
# until the switch is turned off 
player1BasketToggle = 0
player2BasketToggle = 0

    
# check GPIO inputs and alter variables such as score accordingly
def gpioInput():
    global player1Score, player2Score, player1BasketToggle, player2BasketToggle
    input_state_P1BASKET = GPIO.input(GPIO_INPUT_P1BASKET)
    input_state_P2BASKET = GPIO.input(GPIO_INPUT_P2BASKET)
    # Define these inside function or outside function?  Let's try both!    
    if input_state_P1BASKET == False and player1BasketToggle == 0:
        #if input_state_P1BASKET == False:
        player1Score = player1Score + 1
        player1BasketToggle = 1
        gpioOutput(1)
        print('Player 1 Basket')
    if input_state_P1BASKET == True:
        #print('p1 basket off')
        player1BasketToggle = 0
    # if input_state_P2BASKET == False and player2BasketToggle == 0:
    if input_state_P2BASKET == False and player2BasketToggle == 0:
        print('Player 2 Basket')
        print('player 2 toggle' + str(player2BasketToggle))
        player2Score = player2Score + 1
        player2BasketToggle = 1
        gpioOutput(2)
    if input_state_P2BASKET == True:
        # print('p2 basket off')
        player2BasketToggle = 0

# We can safely ignore the events that we don't need.  Ignoring unneeded events
# helps with debugging, since we can print the events occuring without
# being overwhelmed with unneeded data    
pygame.event.set_blocked((pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, 
                          pygame.MOUSEBUTTONDOWN,pygame.WINDOWENTER,pygame.WINDOWLEAVE,pygame.WINDOWLEAVE,pygame.WINDOWFOCUSLOST,pygame.WINDOWTAKEFOCUS))

# The below function outputs signals for lights to the GPIO pins
def gpioOutput(player = 0):
    global player1LightTimeLock, player2LightTimeLock
    if player == 1:
        if pygame.time.get_ticks() >= player1LightTimeLock: 
            GPIO.output(GPIO_OUTPUT_P1LIGHT, GPIO.HIGH) # GPIO 10
            player1LightTimeLock = pygame.time.get_ticks() + lightOnTimeMilliseconds
    if player == 2:
        if pygame.time.get_ticks() >= player2LightTimeLock: 
            GPIO.output(GPIO_OUTPUT_P2LIGHT, GPIO.HIGH)
            player2LightTimeLock = pygame.time.get_ticks() + lightOnTimeMilliseconds
    if player == 0:
        if pygame.time.get_ticks() >= player1LightTimeLock: 
            GPIO.output(GPIO_OUTPUT_P1LIGHT, GPIO.LOW)
        if pygame.time.get_ticks() >= player2LightTimeLock: 
            GPIO.output(GPIO_OUTPUT_P2LIGHT, GPIO.LOW)


def main(gameTimerMinutes, start_ticks):
    clock = pygame.time.Clock()
    # This dict can be left as-is, since pygame will generate a
    # pygame.JOYDEVICEADDED event for every joystick connected
    # at the start of the program.
    joysticks = {}

    done = False
    while not done:
        # Grab Global Variables that we want inside our loop
        global player1Score, player2Score
        gameEndTime = start_ticks + (gameTimerMinutes * 60000)
        timeRemaining = gameEndTime - pygame.time.get_ticks()
        minutesRemaining = math.floor(timeRemaining/60000)
        secondsRemaining = math.floor(timeRemaining/1000)-(minutesRemaining * 60)
        # Event processing step.
        for event in pygame.event.get():
            print(event)
            
            if event.type == pygame.QUIT:
                print('line 170')
                quitGame()

            if event.type == pygame.JOYBUTTONDOWN:
                # A = 1, B = 2,  Start = 9, select = 8
                if event.dict.get('joy')==0:
                    if event.button == 1:
                        gpioOutput(1)
                    
                if event.dict.get('joy')==1:
                    if event.button == 1:
                        gpioOutput(2)

                if event.button == 9:
                    mainMenuShow()
                
            if event.type == pygame.JOYAXISMOTION:
                if event.dict.get('joy')==0:
                    if round(event.dict['value']) == -1 and (event.dict['axis']) == 1: #note: axis is inverted.  Please use -1 for up
                        player1Score = player1Score + 1
                        gpioOutput(1)
                        
                    if round(event.dict['value']) == 1 and (event.dict['axis']) == 1: #note: axis is inverted.  Please use -1 for up
                        player1Score = player1Score - 1
                        if player1Score < 0:
                            player1Score = 0
                            
                if event.dict.get('joy')==1:
                    if round(event.dict['value']) == -1 and (event.dict['axis']) == 1: #note: axis is inverted.  Please use -1 for up
                        player2Score = player2Score + 1
                        gpioOutput(2)
                        
                    if round(event.dict['value']) == 1 and (event.dict['axis']) == 1: #note: axis is inverted.  Please use -1 for up
                        player2Score = player2Score - 1
                        if player1Score < 0:
                            player2Score = 0

            # Handle hotplugging
            if event.type == pygame.JOYDEVICEADDED:
                joy = pygame.joystick.Joystick(event.device_index)
                joysticks[joy.get_instance_id()] = joy
                print(f"Joystick {joy.get_instance_id()} connencted")

            if event.type == pygame.JOYDEVICEREMOVED:
                del joysticks[event.instance_id]
                print(f"Joystick {event.instance_id} disconnected")
                
            if event.type == KEYDOWN and event.key in [K_ESCAPE, K_q,]:
                quitGame()

        # Go ahead and update the screen with what we've draw and limit to 30 frames per second.
        clock.tick(30)
        drawDisplay(minutesRemaining,secondsRemaining,timeRemaining)
        gpioInput()
        gpioOutput()

def drawDisplay(minutesRemaining,secondsRemaining,timeRemaining):
    player1ScoreDisplay = playerScoreFont.render(str(player1Score), True, BLACK)
    player1ScoreDisplayRect = player1ScoreDisplay.get_rect()
    player1ScoreDisplayRect.center = (X/4,Y/2)
    player1NameDisplay = playerNameFont.render(player1Name, True, BLACK)
    player1NameDisplayRect = player1NameDisplay.get_rect()
    player1NameDisplayRect.center = (X/4,Y/10)
    
    player2ScoreDisplay = playerScoreFont.render(str(player2Score), True, BLACK)
    player2ScoreDisplayRect = player2ScoreDisplay.get_rect()
    player2ScoreDisplayRect.center = (3*(X/4),Y/2)
    player2NameDisplay = playerNameFont.render(player2Name, True, BLACK)
    player2NameDisplayRect = player2NameDisplay.get_rect()
    player2NameDisplayRect.center = (3*(X/4),Y/10)
    
    twoDigitSeconds = ("%02d" % (secondsRemaining,))
    timeRemainingDisplay = timerFont.render((str(minutesRemaining) + ':' + str(twoDigitSeconds) ), True, BLACK)
    timeRemainingDisplayRect = timeRemainingDisplay.get_rect()
    timeRemainingDisplayRect.center = (X/2,Y-(Y/10))

    # Drawing step
    # First, clear the screen to white. Don't put other drawing commands
    # above this, or they will be erased with this command.
    screen.fill(background)
    # Now we can send our data to the screen
    screen.blit(player1NameDisplay, player1NameDisplayRect)
    screen.blit(player2NameDisplay, player2NameDisplayRect)
    screen.blit(player1ScoreDisplay, player1ScoreDisplayRect)
    screen.blit(player2ScoreDisplay, player2ScoreDisplayRect)
    if timeRemaining >= 0: # Do not draw time clock if time is <= 0
        screen.blit(timeRemainingDisplay, timeRemainingDisplayRect)

    pygame.display.flip()
    pygame.display.update()


def quitGame():
    print('line 286')
    GPIO.cleanup() 
    pygame.quit()
    sys.exit()
    
def mainMenuShow():
    for event in pygame.event.get():
    # Handle Joystick hotplugging
        if event.type == pygame.JOYDEVICEADDED:
            joy = pygame.joystick.Joystick(event.device_index)
            joysticks[joy.get_instance_id()] = joy
            print(f"Joystick {joy.get_instance_id()} connencted")
        if event.type == pygame.JOYDEVICEREMOVED:
            del joysticks[event.instance_id]
            print(f"Joystick {event.instance_id} disconnected")
    
    def start_the_game():
        start_ticks = pygame.time.get_ticks()
        main(gameTimerMinutes,start_ticks)
    
    def advanced_menu():
        mainmenu._open(advanced)
        
    def setGameTimer(value, minutes):
        global timeRemaining, gameTimerMinutes
        print(value)
        print(minutes)
        # gameEndTime = start_ticks + (minutes * 60000)
        timeRemaining = (minutes * 60000)
        gameTimerMinutes = minutes
        print (timeRemaining)
    
    
    mainmenu = pygame_menu.Menu('Welcome to Rat Basketball!', X, Y, theme=themes.THEME_DARK)
    # mainmenu.add.text_input('Player 1 Name: ', default='Player 1')
    # mainmenu.add.text_input('Player 1 Name: ', default='Player 2')
    mainmenu.add.selector('Game Time (minutes, 0 is infinite): ', [('0', 0),('1', 1), ('2', 2), ('3', 3), ('4', 4), ('5', 5), ('6', 6), ('7', 7), ('8', 8), ('9', 9), ('10', 10)], onchange=setGameTimer)
    mainmenu.add.button('Play', start_the_game)
    # mainmenu.add.button('Advanced Options', advanced_menu)
    mainmenu.add.button('Quit', quitGame)  #mainmenu.add.button('Quit', pygame_menu.events.EXIT)
    # TODO: complete advanced functionality
    # advanced = pygame_menu.Menu('Advanced Options', X, Y, theme=themes.THEME_BLUE)
    # advanced.add.selector('Auto Score :', [('On', 1), ('Off', 0)])  #onchange=set_Autoscore)
    # advanced.add.selector('Auto Feed :', [('On', 1), ('Off', 0)])  #onchange=set_Autoscore)
    # advanced.add.selector('Auto Reinforce (light) :', [('On', 1), ('Off', 0)])  #onchange=set_Autoscore)
    # advanced.add.selector('Auto Light Time): ', [('0', 0),('1', 1), ('2', 2), ('3', 3), ('4', 4), ('5', 5), ('6', 6), ('7', 7), ('8', 8), ('9', 9), ('10', 10)])
    # advanced.add.selector('Score Sound :', [('On', 1), ('Off', 0)])  #onchange=set_Autoscore)
    # advanced.add.selector('Auto Feed :', [('On', 1), ('Off', 0)])  #onchange=set_Autoscore)
    # advanced.add.button('Back', mainMenuShow)
    
    # let's draw an arrow on the screen to highlight our selection    
    arrow = pygame_menu.widgets.LeftArrowSelection(arrow_size = (10, 15))
    
    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                print('line 353')
                quitGame()
    
        if mainmenu.is_enabled():
            mainmenu.update(events)
            mainmenu.draw(screen)
            if (mainmenu.get_current().get_selected_widget()):
                arrow.draw(screen, mainmenu.get_current().get_selected_widget())
    
        pygame.display.update()   

while True:  
    mainMenuShow()

# The below sould never happen.  TODO: program the bellow to be an exception
# to show errors if applicable.  
print('This should have never happened!  Please check configuration')
