OLA Node

this node try to provide an interface to the Open Lighting Architekture Framework (OLA) for AnimationNodes.

its currently in alpha state and only tested under Linux (Kubuntu 16.04)

installation (for linux):
```
# move to your blender addons directory
cd /home/$USER/.config/blender/2.78/scripts/addons/
# clone this repository
git clone --recursive https://github.com/s-light/animation_nodes
```
than install ola for your system:
https://www.openlighting.org/ola/getting-started/downloads/

if you compile from source enable python libs:
```$ ./configure --enable-python-libs```

change path to ola in node.

than it should work ;-)
