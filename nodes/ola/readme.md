OLA Node

this node try to provide an interface to the Open Lighting Architekture Framework (OLA) for AnimationNodes.

its currently in alpha state and only tested under Linux (Kubuntu 16.04)

installation (for linux):
```shell
# move to your blender addons directory
cd /home/$USER/.config/blender/2.78/scripts/addons/
# clone this repository
git clone --recursive https://github.com/s-light/animation_nodes
# install protobuf
$ sudo -H pip3 install protobuf
# try from within the blender python console:
# then copy the protobuf folder from the python install
# to the blender internal python
# /usr/local/lib/python3.5/dist-packages/google/
# to
# INSTALLPATHTOBLENDER/blender-2.78-linux-glibc211-x86_64/2.78/python/lib/python3.5/site-packages/
$ cp -r /usr/local/lib/python3.5/dist-packages/google INSTALLPATHTOBLENDER/blender-2.78-linux-glibc211-x86_64/2.78/python/lib/python3.5/site-packages/
# now you additionally have to install six (needed by protobuf)
# try
$ sudo -H pip3 install six
[sudo] password for stefan:
Requirement already satisfied (use --upgrade to upgrade): six in /usr/lib/python3/dist-packages
# so for me this was already installed in the system. we only need to copy it to the blender python...
# for this note the path that is printed: for me it is /usr/lib/python3/dist-packages (and exchange in the following command..)
# six is contained in a single file so its easy as:
$ cp /usr/lib/python3/dist-packages/six.py INSTALLPATHTOBLENDER/blender-2.78-linux-glibc211-x86_64/2.78/python/lib/python3.5/site-packages/

```

than install ola for your system:
https://www.openlighting.org/ola/getting-started/downloads/

if you compile from source enable python libs:
```$ ./configure --enable-python-libs```

then try if all is setup correctly:
from within blender interactive python console try:
(exchange /home/stefan/ola/python with your ola installation path..)
```python
>>> import sys
>>> sys.path.append('/home/stefan/ola/python')
>>> from ola.ClientWrapper import ClientWrapper
>>> ClientWrapper
<class 'ola.ClientWrapper.ClientWrapper'>

>>>```

than it should work ;-)
