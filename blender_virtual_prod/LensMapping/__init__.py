# ========================================================== Import Addon Modules

modulesNames = ['LensFile', 'LensMapping', 'LensMapping_ui']

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
