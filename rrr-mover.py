#!/usr/bin/python3

from random import random
import re
import sys


filename = sys.argv[1]
rrrdata = open(filename,'r').read()

name,ext = filename.split('.')

lat0 = 47.975453
lon0 = 16.504181




for i in range(10):
    lat = lat0 + (random()-0.5)/10
    lon = lon0 + (random()-0.5)/10
    outfile = f'{name}_{i}.{ext}'
        
    rrrdata0 = rrrdata.replace(f'OSI_Lat {lat0}','OSI_Lat '+str(lat))
    rrrdata0 = rrrdata0.replace(f'OSI_Lon {lon0}',f'OSI_Lon '+str(lon))
    
    print(lat,lon,outfile)
    
    with open(outfile, 'w') as file:
        file.write(rrrdata0)
    file.close()