## Installation Instructions

# Start with a fresh install of Raspberry Pi OS (legacy, 64 bit) Debian Bullseye & Update System Packages:
sudo apt update && sudo apt upgrade -y

# Install or Upgrade pygame and pygame_menu
pip install --upgrade --force-reinstall pygame==2.3.0 

# Install RPi.GPIO
sudo pip install RPi.GPIO

# Install SDL2 Dependencies
sudo apt-get install libsdl2-mixer-2.0-0 python3-sdl2

Without installing the above packages, you will encounter errors
loading the required fonts to run the game, and running the program.  

## Getting the software:

# Clone the repository
git clone https://github.com/ratbasketball/rat_basketball.git

# Move Python files to the desktop
mv rat_basketball/*.py ~/Desktop/

# Clean up by removing the repository folder (optional)
rm -rf rat_basketball
