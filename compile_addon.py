# copy in build folder
import os
import shutil
if os.path.exists("./build_plugin"):
    shutil.rmtree("./build_plugin")
shutil.copytree("./blender_virtual_prod/", "./build_plugin/blender_virtual_prod/")


# compile Freed and Lens code which do not depend on Blender API
#import subprocess
#subprocess.run(["python", "./cython_compile.py", "build_ext", "--inplace"]) 


# remove compiled sources
#os.remove("./build_plugin/blender_virtual_prod/lensMapping/LensFile.py")
#os.remove("./build_plugin/blender_virtual_prod/liveInput/Freed.py")


# package folder into Zip file
shutil.make_archive('blender_virtual_prod', 'zip', root_dir = './build_plugin', base_dir='blender_virtual_prod')