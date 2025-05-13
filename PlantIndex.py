import cv2
import numpy as np
from matplotlib import pyplot as plt

class PlantIndex:
    def __init__(self,rgb,nir):
        self.rgb = rgb
        self.nir = nir
        self.ndvi = self.analysis()
        self.collection = self.get_collection()
    def get_collection(self):
        self.client = DBconnect.DBconnect()
        db = self.client.getdb()
        return db['PlantIndex']    
        
    def analysis(self,img_nir,img_rgb,time):
        height, width, channels = img_nir.shape # h = 2464, w = 3280

        img_rgb = cv2.resize(img_rgb,(width,height),cv2.INTER_CUBIC)
        image_align = self.image_alignment(img_nir, img_rgb)
       
        img_float = img_rgb.astype(np.float64)
        
        red = img_float[:,:,2]
        print (img_float.shape)
        if len(image_align.shape) == 3: 
            print("gray")
            nir_float = image_align.astype(np.float64)
            nir = nir_float[:,:,2]
        else: 
            nir = image_align
        np.seterr(divide='ignore', invalid='ignore')

        ndvi = (nir.astype(float) - red.astype(float) ) / (nir + red+ 1e-10)
        ndvi = np.divide(
            (nir - red),
            (nir + red + 1e-10),  #
            out=np.zeros_like(nir, dtype=float),
            where=(nir + red) != 0
        )
        plt.imsave(
            f'ndvi_{time}.png',          
            ndvi,                       
            cmap='RdYlGn',              
            vmin=-1,                    
            vmax=1,                     
            origin='upper',             
            dpi=300                     
        )
        
    def image_alignment(self,img_nir,img_rgb):
        sift = cv2.SIFT_create()
        kp1, des1 = sift.detectAndCompute(img_nir, None)
        kp2, des2 = sift.detectAndCompute(img_rgb, None)
        
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)
    
        matches = flann.knnMatch(des1, des2, k=2)

        good_matches = []
        for m, n in matches:
            if m.distance < 0.9 * n.distance:
                good_matches.append(m)
       
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        filtered_matches = filter_matches_with_mask(good_matches, mask)
        
        img_warp = cv2.warpPerspective(img_nir, H, (width,height))
        return img_warp
