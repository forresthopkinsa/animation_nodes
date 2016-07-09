SerialPort Node

this node try to provide an interface to a hw serial port for AnimationNodes.

its currently in alpha state and only tested under Linux (Kubuntu 16.04)

installation (for linux):
```
# move to your blender addons directory
cd /home/$USER/.config/blender/2.77/scripts/addons/
# clone this repository
git clone --recursive https://github.com/s-light/animation_nodes
# install python - the same version as in blender internally used
sudo apt-get install python3
# install pip3
sudo apt-get install python3-pip
# install pyserial
sudo -H pip3 install pyserial
# then copy the pyserial folder from the python install
# to the blender internal python
# /usr/local/lib/python3.5/dist-packages/serial/
# to
# INSTALLPATHTOBLENDER/blender-2.77a-linux-glibc211-x86_64/2.77/python/lib/python3.5/site-packages/
```

than it should work ;-)
