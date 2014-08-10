import math

def scale2zoom(scale):
    baseZoomLevel = 20
    baseScale = 500
    
    for i in range(20):
        if scale <= baseScale << i:
            return baseZoomLevel-i
    
    return 0
    
def latlng2xy(lat, lng,  zoom):
  latRad = math.radians(lat)
  n = 2.0 ** zoom
  x = int((lng + 180.0) / 360.0 * n)
  y = int((1.0 - math.log(math.tan(latRad) + (1 / math.cos(latRad))) / math.pi) / 2.0 * n)
  
  return (x, y)