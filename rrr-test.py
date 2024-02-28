import json
import re
lat = None
lon = None
osirelevantfound = False
sampleid = None
rrr_data = {}
rrr_data['nuclides']={}
rrr_data['attributes']={}
filename = "C:/Users/morten/rrr_244 (002).txt"
layer = QgsProject.instance().mapLayersByName('rrr')[0]
pr = layer.dataProvider()
rrr = open(filename,'r').read()
attributes = {}
readquantified = False
lines = rrr.split('\n')
for idx,line in enumerate(lines):
    line = line.strip()
    if sampleid is None and line.startswith('Sample ID:'):
        data = re.split(r"\s{2,}",line)
        sampleid = data[1]
        print(f'Sample ID: {sampleid}')
        continue
    if line.startswith('OSI_'):
        print(idx,line)
        if ' ' in line:
            (k,v) = line.split(' ',1)
        else:
            k = line
            v = line[idx+1]
        (OSI,k) = k.split('_')
        k = k.strip()
        v = v.strip()
        if k == 'Lat':
            lat = float(v)
        if k == 'Lon':
            lon = float(v)
        print(k,v)
        attributes[k] = v
    
    elif readquantified or line == 'Nuclides Quantified:':
        if line.startswith('Nuclide'):
            if line == 'Nuclides Quantified:':
                readquantified = True
                continue
            else:
                headers = re.split(r"\s{2,}",line)
                continue
        elif line.endswith(':'):
            readquantified = False
            continue
        data = re.split(r"\s{2,}",line)
       
        if len(data) > 2:
            line = {}
            for idx,head in enumerate(headers):
                line[head]=data[idx]
            rrr_data['nuclides'][line['Nuclide']] = line
if not (lat is None or lon is None):
    rrr_data['attributes']=attributes
    insdata = [None,rrr,json.dumps(rrr_data),filename,osirelevantfound,sampleid,attributes['SampleType'],attributes['MissionCode'],attributes['BarCode']]
    feature = QgsFeature()
    point=QgsPointXY(float(lon),float(lat))
    geom=QgsGeometry.fromPointXY(point)
    feature.setGeometry(geom)
    # Fixes attibs later:
    feature.setAttributes(insdata)
    pr.addFeatures( [ feature ] )
