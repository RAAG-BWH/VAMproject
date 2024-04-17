# VAM project

This project is about computational tomography, its core libraries are **ASTRA Toolbox** and **VAMToolbox**

## Installation
The file **vamapp.yml** is the environment for windows (cronjobs are not supported), **vamapp_linux.yml** is the environment for development in Ubuntu 22.04.4 and **VAMenv2_deploy.yml** is the environment for the AWS cluster. The command for installation is:
```
conda env create -f VAMenv2_deploy.yml
```

## Errors thrown
The error `Error: pyglet.canvas.xlib.NoSuchDisplayException: Cannot connect to "None"` is always thrown in an environment when the GUI is not available (during the deployment to the server), the following commands solved the issue:
```
sudo apt-get update
sudo apt-get install xvfb
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
```