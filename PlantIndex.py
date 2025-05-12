import cv2


class PlantIndex:
    def __init__(self,rgb,nir):
        self.rgb = rgb
        self.nir = nir
        self.ndvi = self.analysis()
        
    def analysis(self):
        
        
    def image_alignment(self):
        