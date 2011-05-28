
# python conversor.py > data.json

import csv
import json
from hashlib import md5


def center(coordinates):
    """
    >>> [[0,0],[2, 2]]
    (1.0, 1.0)
    """
    l = float(len(coordinates))
    return (sum((c[0] for c in coordinates))/l, sum(c[1] for c in coordinates)/l)
    
def municipalities_latlon_old(data):
    mun = json.loads(data)
    mun_positions = {}
    for m in mun['rows']:
        geom = json.loads(m['the_geom'])
        coordinates = geom['coordinates'][0][0][:-1]
        c = center(coordinates)
        mun_positions[m['name'].lower()] = c
    return mun_positions

def municipalities_latlon(data):
    mun = json.loads(data)
    mun_positions = {}
    for m in mun:
        mun_positions[m['municipio'].lower()] = (m['center_latitude'], m['center_longitude'])
    return mun_positions
        
        
def municipalities_results(f):
    mun = {}
    r = csv.reader(f, delimiter=',', quotechar='"')
    headers = list(r.next())
    for row in r:
        d = dict(zip(headers, row))
        mun[d['municipality_name'].lower().decode('utf-8')] =  d
    return mun
        
m1 = municipalities_latlon(open('municipalities.json').read())
m2 = municipalities_results(open('prov_muni_hydra.csv'))

def smoothstep(a, b, t):
    if(t < a): 
        return 0.0
    if(t > b): 
        return 1.0

    t = (t-a)/(b-a);
    return (t) * (t) * (3 - 2*(t))

from collections import Counter, defaultdict
#print Counter((x['primer_partido_nombre'] for x in m2.values()))

def filter_partido(s):
    if "P.P." in s or "PP" in s or "P.P" in s:
        return "PP"
    elif "P.S.O.E." in s or "PSOE" in s:
        return "PSOE"
    elif "CiU" in s or "CIU" in s:
        return "CIU"
    return s



def string_to_html_color(s):
  return md5(s.encode('ascii','ignore')).hexdigest()[:6];

pueblo_partido = {}
for k,m in m2.iteritems():
    pueblo_partido[k] =  filter_partido(m['primer_partido_nombre'])

colors = {'PP': '0199cb', 
          'PSOE': 'f60400',
          'CIU': '993400',
          'B.N.G': 'fe9833'}

def mas_votado(data):
    t = float(data['primer_votos'])
    t = smoothstep(100, 200000, t)
    return (t*20, None)#to_color(t))

def mas_votado_percent(data):
    t = float(data['primer_percent'])
    return t*0.01, to_color(t)

def to_color(t):
    return  "0x00%02x00" % int(t*255)

def nulos(data):
    t = float(data['votos_nulos_percent'])
    t = smoothstep(0, 10, t)
    return t*2.0, to_color(t)

def blancos(data):
    t = float(data['votos_en_blanco_percent'])
    t = smoothstep(0, 10, t)
    return t*2.0, to_color(t)

def concejales(data):
    try:
        t = float(data['concejales_a_elegir'])
    except:
        return 0, None
    #t = smoothstep(0, 200, t)
    return t*.001, None
    

def vis(fn):
    
    data = []
    for x in m1:
        if x in m2:
            partido = pueblo_partido[x]
            if partido in colors:
                c = colors[partido]
            else:
                c = string_to_html_color(partido.decode('utf-8'))
            c = "0x"+c

            data.append(m1[x][0])
            data.append(m1[x][1])
            t, cc = fn(m2[x])
            if cc != None:
                c = cc
            data.append(t)
            data.append(c)
    return data
        
data = vis(mas_votado)
data2 = vis(nulos)
data3 = vis(blancos)
data4 = vis(concejales)
print json.dumps([['partido mas votado', data],['% blancos', data3], ['% nulos', data2], ['concejales a elegir', data4]])

        
