# blender-virtual-prod-plugin

A utility blender plugin to simplify virtual production workflows.

There are 3 components:
- Lens Mapping : Read a lens file and make it available as blender drivers conversion functions
- Live Input : Receive tracking data using the FreeD protocol
- Post Prod Tools : Customizable compositing presets to work with real camera plates 


## install the add-on

in Blender, go to edit->preferences->add-on\
click the "install" button\
select the zip file and proceed\
check the box to activate the add-on.

In the Scene menu, a "[BVP] Live FreeD Input" panel should have appeared.\
In the Scene menu, a "[BVP] Lens Mapping" panel should have appeared.\
In the Output menu, a "[BVP] Post Prod Tools" panel should have appeared.


## compile add-on

run compile_addon.py from the root of the git repository\
this will generate a zip file whih can be installed in Blender.

