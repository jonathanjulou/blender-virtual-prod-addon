bl_info = {
    "name": "Virtual Prod",
    "description": "",
    "author": "Jonathan Julou",
    "version": (2, 0, 0),
    "blender": (4, 1, 0),
    "location": "3D View > Scene",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": "Camera"
}

# https://b3d.interplanety.org/en/creating-multifile-add-on-for-blender


# ========================================================== Import Addon Modules

modulesNames = ['LiveInput', 'LensMapping', 'PostProdTools']

modulesFullNames = []
for currentModuleName in modulesNames:
    modulesFullNames.append('{}.{}'.format(__name__, currentModuleName))


import sys
import importlib

for currentModuleFullName in modulesFullNames:
    if currentModuleFullName in sys.modules:
        importlib.reload(sys.modules[currentModuleFullName])
    else:
        globals()[currentModuleFullName] = importlib.import_module(currentModuleFullName)
        setattr(globals()[currentModuleFullName], 'modulesNames', modulesFullNames)




# ========================================================== Registration

def register():
    for currentModuleName in modulesFullNames:
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'register'):
                sys.modules[currentModuleName].register()


def unregister():
    for currentModuleName in modulesFullNames:
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'unregister'):
                sys.modules[currentModuleName].unregister()



if __name__ == "__main__":
    register()
