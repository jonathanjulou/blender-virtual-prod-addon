"""
Copyright Miraxyz 2024

Defines class LensFile which can be used to load the EZprofile OpenLensFile JSON export.

The object has to be initalized first, loading the lens file in memory and creating the interpolators.
Then the getter methods can be used with current FIZ encoder data to recover calibrated values.
"""

import os
import json
import numpy as np

from bisect import bisect_left
from functools import partial



def tryGetPairFromDict(data, focus, zoom):
    if focus in data.keys():
        if zoom in data[focus].keys():
            return data[focus][zoom]
    return 0
    
    
def tryGetPairFromFocusDict(data, focus, zoom):
    if focus in data.keys():
        return data[focus]
    return 0


def computeTransformCoeff(k, ind, wi, wo):
    """
        Compute the distortion transformation between
        the two spaces and return it
    """
    if(wi==wo):
        return k
    return k*((wi / wo)**(2*ind))
    


# evaluate polynom 2d at (x,y)
def evaluate_polynom_2d(polynom, x_degree, y_degree, x, y):
    polynomShape = (x_degree+1,y_degree+1)

    # compute value at (x,y)
    value = np.polynomial.polynomial.polyval2d(x, y, polynom.reshape(polynomShape))  
    
    return value



class RegularGridInterpolator:

    def __init__(self, x, y, z):
        self.xT = x
        self.yT = y
        self.zT = z
        
        
    def __call__(self, x, y):
        i = bisect_left(self.xT, x) - 1
        j = bisect_left(self.yT, y) - 1

        x1 = self.xT[i]
        try:
            x2 = self.xT[i + 1]
        except:
            x2 = self.xT[i]
            
        y1 = self.yT[j]
        try:
            y2 = self.yT[j + 1]
        except:
            y2 = self.yT[j]
        
        
        z11 = self.zT[i][j]
        try:
            z12 = self.zT[i][j + 1]
        except:
            z12 = self.zT[i][j]
        
        try:
            z21 = self.zT[i + 1][j]
            try:
                z22 = self.zT[i + 1][j + 1]
            except:
                z22 = self.zT[i + 1][j]
        except:
            z21 = self.zT[i][j]
            try:
                z22 = self.zT[i][j + 1]
            except:
                z22 = self.zT[i][j]

        return (z11 * (x2 - x) * (y2 - y) +
                z21 * (x - x1) * (y2 - y) +
                z12 * (x2 - x) * (y - y1) +
                z22 * (x - x1) * (y - y1)) / ((x2 - x1) * (y2 - y1))



class LensFile:

    def __init__(self, filename=None):
        self.initialized = False
        self.initialize(filename)
        
        self.sensorWidth = None
        self.sensorHeight = None
        

    def initialize(self, filename):
        self.filename = filename

        self.data = None

        self.focalMMInterpolator = None
        self.focalPixInterpolator = None
        self.focusDistInterpolator = None
        self.K1UInterpolator = None
        self.K2UInterpolator = None
        self.K1DInterpolator = None
        self.K2DInterpolator = None
        self.nodalInterpolator = None
        
        self.zoomEncoderMin = 0
        self.zoomEncoderMax = 65535
        self.focusEncoderMin = 0
        self.focusEncoderMax = 65535

        if filename is not None:
            self.readLensFile(self.filename)
            self.initialized = True
            

    def reset(self):
        self.data = None
        self.focalPixInterpolator = None
        self.focalMMInterpolator = None
        self.focusDistInterpolator = None
        self.K1UInterpolator = None
        self.K2UInterpolator = None
        self.K1DInterpolator = None
        self.K2DInterpolator = None
        self.nodalInterpolator = None


    def readGtsamLensFile(self, filename):
        self.filename = filename

        # read lens file if is not None
        if filename is not None:
            with open(filename, "r") as f:
                self.data = json.load(f)

            try:
                self.sensorWidth = self.data["SensorSize"][0]
                self.sensorHeigth = self.data["SensorSize"][1]
                
                # load encoder bounds
                self.zoomEncoderMin = 0
                self.zoomEncoderMax = 65535
                self.focusEncoderMin = 0
                self.focusEncoderMax = 65535
                if "EncoderBounds" in self.data.keys():
                    if self.data["EncoderBounds"][0] != []:
                        self.zoomEncoderMin = int(self.data["EncoderBounds"][0][0])
                        self.zoomEncoderMax = int(self.data["EncoderBounds"][0][1])
                    if self.data["EncoderBounds"][1] != []:
                        self.zoomEncoderMin = int(self.data["EncoderBounds"][1][0])
                        self.zoomEncoderMax = int(self.data["EncoderBounds"][1][1])

                self.focalPixInterpolator  = None
                self.focalMMInterpolator   = partial(evaluate_polynom_2d, self.data["Focal"]["coefficient"], self.data["Focal"]["kx"], self.data["Focal"]["ky"])
                self.focusDistInterpolator = partial(evaluate_polynom_2d, [0,0], 0, 0)
                self.K1UInterpolator       = partial(evaluate_polynom_2d, self.data["K1"]["coefficient"], self.data["K1"]["kx"], self.data["K1"]["ky"])
                self.K2UInterpolator       = partial(evaluate_polynom_2d, self.data["K2"]["coefficient"], self.data["K2"]["kx"], self.data["K2"]["ky"])
                self.K1DInterpolator       = partial(evaluate_polynom_2d, self.data["K1"]["coefficient"], self.data["K1"]["kx"], self.data["K1"]["ky"])
                self.K2DInterpolator       = partial(evaluate_polynom_2d, self.data["K2"]["coefficient"], self.data["K2"]["kx"], self.data["K2"]["ky"])
                self.nodalInterpolator     = partial(evaluate_polynom_2d, self.data["Nodal"]["coefficient"], self.data["Nodal"]["kx"], self.data["Nodal"]["ky"])

            # wrong json format, not an open lens profile
            except KeyError as e:
                print(e)
                self.reset()

        else:
            self.reset()


    def readOpenLensFile(self, filename):
        self.filename = filename

        # read lens file if is not None
        if filename is not None:
            with open(filename, "r") as f:
                self.data = json.load(f)

            try:
                self.sensorWidth = self.data["SensorSizeMillimetre"][0]
                self.sensorHeigth = self.data["SensorSizeMillimetre"][1]
                
                # load encoder bounds
                self.zoomEncoderMin = 0
                self.zoomEncoderMax = 65535
                self.focusEncoderMin = 0
                self.focusEncoderMax = 65535
                if "EncoderBounds" in self.data.keys():
                    if "Zoom" in self.data["EncoderBounds"].keys():
                        if "ZoomMin" in self.data["EncoderBounds"]["Zoom"].keys():
                            self.zoomEncoderMin = int(self.data["EncoderBounds"]["Zoom"]["ZoomMin"])
                        if "ZoomMax" in self.data["EncoderBounds"]["Zoom"].keys():
                            self.zoomEncoderMax = int(self.data["EncoderBounds"]["Zoom"]["ZoomMax"])
                    if "Focus" in self.data["EncoderBounds"].keys():
                        if "FocusMin" in self.data["EncoderBounds"]["Focus"].keys():
                            self.focusEncoderMin = int(self.data["EncoderBounds"]["Focus"]["FocusMin"])
                        if "FocusMax" in self.data["EncoderBounds"]["Focus"].keys():
                            self.focusEncoderMax = int(self.data["EncoderBounds"]["Focus"]["FocusMax"])

                x = np.array(sorted(list(self.data["PinholeIntrinsics"]["FocalLengthPix"].keys())))
                y = np.array(sorted(list(self.data["PinholeIntrinsics"]["FocalLengthPix"][x[0]].keys())))

                extBoundMin = -2**24-1
                extBoundMax = 2**24+1

                if x.astype(float)[0] < 0.5:
                    xf = np.concatenate([[extBoundMin], x.astype(float), [extBoundMax]])
                else:
                    xf = np.concatenate([[extBoundMax], x.astype(float), [extBoundMin]])
                if y.astype(float)[0] < 0.5:
                    yf = np.concatenate([[extBoundMin], y.astype(float), [extBoundMax]])
                else:
                    yf = np.concatenate([[extBoundMax], y.astype(float), [extBoundMin]])
                xg, yg = np.meshgrid(xf, yf, indexing='ij', sparse=True)

                dataFocalPix = []
                dataFocalMM = []
                dataFocusDist = []
                dataK1U = []
                dataK2U = []
                dataK1D = []
                dataK2D = []
                dataN = []
                for f in x:
                    dataFocalPix.append([])
                    dataFocalMM.append([])
                    dataFocusDist.append([])
                    dataK1U.append([])
                    dataK2U.append([])
                    dataK1D.append([])
                    dataK2D.append([])
                    dataN.append([])
                    for z in y:
                        dataFocalPix[-1].append(tryGetPairFromDict(self.data["PinholeIntrinsics"]["FocalLengthPix"], f, z))
                        dataFocalMM[-1].append(tryGetPairFromDict(self.data["PinholeIntrinsics"]["FocalLengthMillimetre"], f, z))
                        dataFocusDist[-1].append(tryGetPairFromFocusDict(self.data["FocusDistanceMetre"], f, z))
                        dataK1U[-1].append(tryGetPairFromDict(self.data["Undistortion"]["K1"], f, z))
                        dataK2U[-1].append(tryGetPairFromDict(self.data["Undistortion"]["K2"], f, z))
                        dataK1D[-1].append(tryGetPairFromDict(self.data["Distortion"]["K1"], f, z))
                        dataK2D[-1].append(tryGetPairFromDict(self.data["Distortion"]["K2"], f, z))
                        dataN[-1].append(tryGetPairFromDict(self.data["EntrancePupilDistanceMetre"], f, z))

                # extend bounds to avoid landing out of interpolatable domain
                dataFocalPix = [dataFocalPix[0]] + dataFocalPix + [dataFocalPix[-1]]
                dataFocalMM = [dataFocalMM[0]] + dataFocalMM + [dataFocalMM[-1]]
                dataFocusDist = [dataFocusDist[0]] + dataFocusDist + [dataFocusDist[-1]]
                dataK1U = [dataK1U[0]] + dataK1U + [dataK1U[-1]]
                dataK2U = [dataK2U[0]] + dataK2U + [dataK2U[-1]]
                dataK1D = [dataK1D[0]] + dataK1D + [dataK1D[-1]]
                dataK2D = [dataK2D[0]] + dataK2D + [dataK2D[-1]]
                dataN = [dataN[0]] + dataN + [dataN[-1]]
                for i,_ in enumerate(dataFocalPix):
                    dataFocalPix[i] = [dataFocalPix[i][0]] + dataFocalPix[i] + [dataFocalPix[i][-1]]
                    dataFocalMM[i] = [dataFocalMM[i][0]] + dataFocalMM[i] + [dataFocalMM[i][-1]]
                    dataFocusDist[i] = [dataFocusDist[i][0]] + dataFocusDist[i] + [dataFocusDist[i][-1]]
                    dataK1U[i] = [dataK1U[i][0]] + dataK1U[i] + [dataK1U[i][-1]]
                    dataK2U[i] = [dataK2U[i][0]] + dataK2U[i] + [dataK2U[i][-1]]
                    dataK1D[i] = [dataK1D[i][0]] + dataK1D[i] + [dataK1D[i][-1]]
                    dataK2D[i] = [dataK2D[i][0]] + dataK2D[i] + [dataK2D[i][-1]]
                    dataN[i] = [dataN[i][0]] + dataN[i] + [dataN[i][-1]]

                self.focalPixInterpolator = RegularGridInterpolator(xf, yf, dataFocalPix)
                self.focalMMInterpolator = RegularGridInterpolator(xf, yf, dataFocalMM)
                self.focusDistInterpolator = RegularGridInterpolator(xf, yf, dataFocusDist)
                self.K1UInterpolator = RegularGridInterpolator(xf, yf, dataK1U)
                self.K2UInterpolator = RegularGridInterpolator(xf, yf, dataK2U)
                self.K1DInterpolator = RegularGridInterpolator(xf, yf, dataK1D)
                self.K2DInterpolator = RegularGridInterpolator(xf, yf, dataK2D)
                self.nodalInterpolator = RegularGridInterpolator(xf, yf, dataN)

            # wrong json format, not an open lens profile
            except KeyError as e:
                print(e)
                self.reset()

        else:
            self.reset()
            
            
    def readLensFile(self, filename):
        if filename.endswith(".json") or filename.endswith(".ezpinternal"):
            return self.readOpenLensFile(filename)
        elif filename.endswith(".gtsam"):
            return self.readGtsamLensFile(filename)
    
    
    def getEncoderBounds(self):
        return [[self.zoomEncoderMin, self.zoomEncoderMax], [self.focusEncoderMin, self.focusEncoderMax]]
        
        
    def normalizeEncoderValues(self, focus, zoom):
        nFocus = (focus - self.focusEncoderMin) / (self.focusEncoderMax - self.focusEncoderMin)
        nZoom = (zoom - self.zoomEncoderMin) / (self.zoomEncoderMax - self.zoomEncoderMin)
        return nFocus, nZoom


    def getLensName(self):
        if self.data is not None:
            return self.data["LensName"]
        return None


    def getSensorWidth(self):
        return self.sensorWidth


    def getSensorHeight(self):
        return self.sensorHeight


    def getImageWidth(self):
        if self.data is not None:
            return self.data["CalibrationResolution"][0]
        return None


    def getImageHeight(self):
        if self.data is not None:
            return self.data["CalibrationResolution"][1]
        return None


    def getCx(self):
        return None


    def getCy(self):
        return None


    def getCxPix(self):
        if self.data is not None:
            return self.data["PinholeIntrinsics"]["CenterShiftPix"]["Cx"]
        return None


    def getCyPix(self):
        if self.data is not None:
            return self.data["PinholeIntrinsics"]["CenterShiftPix"]["Cy"]
        return None


    def getFocalPix(self, zoom, focus):
        if self.focalPixInterpolator is not None:
            return float(self.focalPixInterpolator(*self.normalizeEncoderValues(focus, zoom)))
        return None
        
        
    def getFocalMM(self, zoom, focus):
        if self.focalMMInterpolator is not None:
            return float(self.focalMMInterpolator(*self.normalizeEncoderValues(focus, zoom)))
        return None
        
        
    def getFocusDistanceM(self, zoom, focus):
        if self.focusDistInterpolator is not None:
            return float(self.focusDistInterpolator(*self.normalizeEncoderValues(focus, zoom)))
        return None
        
        
    def getFocusDistanceM_INFINITY(self, zoom, focus):
        f,z = self.normalizeEncoderValues(focus, zoom)
        f_dist_max = 10000 # metres
    
        if self.focusDistInterpolator is not None:
            if f < 0.95:
                return float(self.focusDistInterpolator(f,z))
            else:
                k = ((f-0.95)/(1-0.95))**10
                return float(self.focusDistInterpolator(f,z))*(1-k) + k*f_dist_max
        return None


    def getK1UndistortOCV(self, zoom, focus):
        if self.K1UInterpolator is not None:
            return float(self.K1UInterpolator(*self.normalizeEncoderValues(focus, zoom)))
        return None


    def getK2UndistortOCV(self, zoom, focus):
        if self.K2UInterpolator is not None:
            return float(self.K2UInterpolator(*self.normalizeEncoderValues(focus, zoom)))
        return None
        
        
    def getK1DistortOCV(self, zoom, focus):
        if self.K1DInterpolator is not None:
            return float(self.K1DInterpolator(*self.normalizeEncoderValues(focus, zoom)))
        return None


    def getK2DistortOCV(self, zoom, focus):
        if self.K2DInterpolator is not None:
            return float(self.K2DInterpolator(*self.normalizeEncoderValues(focus, zoom)))
        return None
        
        
    def getK1UndistortWidthNormalized(self, zoom, focus):
        if self.K1UInterpolator is not None:
            k1 = float(self.K1UInterpolator(*self.normalizeEncoderValues(focus, zoom)))
            
            pix_wi = self.getImageWidth()
            fx = self.getFocalPix(zoom, focus)
            return computeTransformCoeff(k1, 1, pix_wi/fx, 1) # opencv has space width of pix_wi/fx, while width normalization has width 1
        return None


    def getK2UndistortWidthNormalized(self, zoom, focus):
        if self.K2UInterpolator is not None:
            k2 =  float(self.K2UInterpolator(*self.normalizeEncoderValues(focus, zoom)))
            
            pix_wi = self.getImageWidth()
            fx = self.getFocalPix(zoom, focus)
            return computeTransformCoeff(k2, 2, pix_wi/fx, 1) # opencv has space width of pix_wi/fx, while width normalization has width 1
        return None
        
        
    def getK1DistortWidthNormalized(self, zoom, focus):
        if self.K1DInterpolator is not None:
            k1 = float(self.K1DInterpolator(*self.normalizeEncoderValues(focus, zoom)))
            
            pix_wi = self.getImageWidth()
            fx = self.getFocalPix(zoom, focus)
            return computeTransformCoeff(k1, 1, pix_wi/fx, 1) # opencv has space width of pix_wi/fx, while width normalization has width 1
        return None


    def getK2DistortWidthNormalized(self, zoom, focus):
        if self.K2DInterpolator is not None:
            k2 = float(self.K2DInterpolator(*self.normalizeEncoderValues(focus, zoom)))
            
            pix_wi = self.getImageWidth()
            fx = self.getFocalPix(zoom, focus)
            return computeTransformCoeff(k2, 2, pix_wi/fx, 1) # opencv has space width of pix_wi/fx, while width normalization has width 1
        return None


    def getK3(self, zoom, focus):
        if self.data is not None:
            return 0
        return None


    def getP1(self, zoom, focus):
        if self.data is not None:
            return 0
        return None


    def getP2(self, zoom, focus):
        if self.data is not None:
            return 0
        return None


    def getNodal(self, zoom, focus):
        if self.nodalInterpolator is not None:
            return float(self.nodalInterpolator(*self.normalizeEncoderValues(focus, zoom)))
        return None


    def getFileName(self):
        return self.filename


    def isValid(self):
        return self.data is not None





# test when called from command line to validate the LensFile class
if __name__ == "__main__":
    print("start LensFile module tests")
    
    lens_file = LensFile("ARRIUltraPrime32_02.json")
    
    # if calibrated with eztrack external encoders should return 0-65535 in most cases
    print("- Encoder Bounds")
    print("  zoom:", lens_file.getEncoderBounds()[0])
    print("  focus:", lens_file.getEncoderBounds()[1])
    
    
    # estimate the focal length from the focus level. You can just put 0 in the field for zoom
    print("- Encoder Bounds")
    print("  focal length at focus 0:", lens_file.getFocalMM(0, 0), "mm")
    print("  focal length at focus 65535:", lens_file.getFocalMM(0, 65535), "mm")
    
    
    # estimate the focus distance from the focus level. You can just put 0 in the field for zoom
    print("- Encoder Bounds")
    print("  focus distance at focus 0:", lens_file.getFocusDistanceM(0, 0), "m")
    print("  focus distance at focus 30000:", lens_file.getFocusDistanceM(0, 30000), "m")
    print("  focus distance at focus 60000:", lens_file.getFocusDistanceM(0, 60000), "m")
    print("  focus distance at focus 63000:", lens_file.getFocusDistanceM(0, 63000), "m")
    print("  focus distance at focus 64000:", lens_file.getFocusDistanceM(0, 64000), "m")
    print("  focus distance at focus 65000:", lens_file.getFocusDistanceM(0, 65000), "m")
    print("  focus distance at focus 65200:", lens_file.getFocusDistanceM(0, 65200), "m")
    print("  focus distance at focus 65535:", lens_file.getFocusDistanceM(0, 65535), "m")
    
    
    # modified focus function to stretch to a larger value at the end
    print("- Encoder Bounds")
    print("  focus distance at focus 0:", lens_file.getFocusDistanceM_INFINITY(0, 0), "m")
    print("  focus distance at focus 30000:", lens_file.getFocusDistanceM_INFINITY(0, 30000), "m")
    print("  focus distance at focus 60000:", lens_file.getFocusDistanceM_INFINITY(0, 60000), "m")
    print("  focus distance at focus 63000:", lens_file.getFocusDistanceM_INFINITY(0, 63000), "m")
    print("  focus distance at focus 64000:", lens_file.getFocusDistanceM_INFINITY(0, 64000), "m")
    print("  focus distance at focus 65000:", lens_file.getFocusDistanceM_INFINITY(0, 65000), "m")
    print("  focus distance at focus 65200:", lens_file.getFocusDistanceM_INFINITY(0, 65200), "m")
    print("  focus distance at focus 65535:", lens_file.getFocusDistanceM_INFINITY(0, 65535), "m")
    
    
    # get K1 and K2 for undistortion in width normalized space (applied to image UVs)
    # use your current focus instead of 30000
    print("- Undistortion Coefficients")
    print("  K1 for undistortion in width normalized space:", lens_file.getK1UndistortWidthNormalized(0, 30000))
    print("  K2 for undistortion in width normalized space:", lens_file.getK2UndistortWidthNormalized(0, 30000))
    
    # get K1 for distortion in width normalized space (applied to image UVs)
    print("- Distortion Coefficients")
    print("  K1 for distortion in width normalized space:", lens_file.getK1DistortWidthNormalized(0, 30000))
    print("  K2 for distortion in width normalized space:", lens_file.getK2DistortWidthNormalized(0, 30000))
    # note that going from distort to undistort is not a simple sign inversion, the inversion operation is non-linear and usually involves sampling points in 2D image space to compute the inverse mapping
    # Nuke probably has a way to inverse coefficients on their own. They would require either distortion or undistortion coefs depending on their algorithm.
    # if using image UVs, undistortion is done with undistortion coefs, but if done dorectly on image pixels the other one would have to be used.
   
    
    print("end LensFile module tests")