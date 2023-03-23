We need a pygame pygame version greater than 1.9.6, which comes standard
on the raspberry pi as of March 2023.  Please verify that later releases
of the pi operating system do not come standard with a suitable release of
pygame.  

In order to install a later version of pygame we need to run:
	pip install --upgrade --force-reinstall pygame
	
To test the install, open a terminal and start python by typing
	python
	
Now, import pygame by typing:
	import pygame
	
You should recieve a response saying:
	pygame 2.3.0 (SDL 2.24.2, Python 3.9.2)

This is the version we want.  If pygame has been updated and the new version
no longer works with this code, you will have to explicity tell PIP which 
version of pygame to install.  

Now we need to install pygame_menu.  To do this, we will type (in a new terminal):
	pip install pygame_menu
	
As with pygame, we can check the installed version.  
To test the install, open a terminal and start python by typing
	python  

Now, import pygame_menu by typing:
	import pygame_menu
	
You should recieve a response saying:
	pygame-menu 4.3.9
	
The program may run with later versions, but if you experience issues, 
please install the versions we've tested the program with.  

To wrap things up, we need to run two more commands (in a new terminal):
	sudo apt-get install libsdl2-mixer-2.0-0
	sudo apt-get install python3-sdl2

Without installing the above two packages, you will encounter errors
loading the required fonts to run the game.  