import urllib.request
import numpy as np
import pandas as pd
import time, os, stat

def format_exp(string):
    flag = ""
    part = string.strip()
    if string[0] == "-":
        # Put a - at the front of the final string
        flag = "-"
        part = string[1:]
    sgn = part[-2]
    parts = part.split(sgn) # sgn is either + or -, so we will need to accomodate for both cases.
    return float(flag + "0." + parts[0] + "e" + sgn + parts[1])


class TLE:
    """
    Datatype to represent a Two-Line Element Set as a python object
    """
    def __init__(self, sat, line1, line2):
        ## Metadata (line 1) ##
        satnum = line1[2:7]
        classification = line1[7]
        designator = {'year': int(line1[9:11]),
                      'launch': int(line1[11:14]),
                      'piece': line1[14:17].strip()}
        add = 1900
        if designator['year'] < 60:
            add = 2000
        designator['year'] += add
        epoch = int(line1[18:20]) + 2000
        epoch_day = float(line1[20:32])
        half_dndt = float(line1[33:43].replace(".", "0."))
        sixth_d2ndt2 = format_exp(line1[44:52])
        bstar = format_exp(line1[53:61])
        ephemeris = line1[62]
        setnum = line1[64:68]
        
        ## Keplerian Elements ##
        i = float(line2[9:17].strip())
        om = float(line2[17:25].strip())
        e = float('0.' + line2[26:33].strip())
        w = float(line2[34:42].strip())
        M = float(line2[43:51].strip())
        n = float(line2[52:63].strip())
        rev_num = int(line2[63:68].strip())
        
        epoch = pd.Timestamp(day=1,month=1,year=epoch) + pd.to_timedelta(epoch_day, unit='D')
        
        self.__data = {
            'info': {
                    'name': sat,
                    'number': satnum,
                    'classification': classification,
                    'designation': designator,
                    'epoch': str(epoch),
                    '1/2 dn/dt': half_dndt,
                    '1/6 d2n/dt2': sixth_d2ndt2,
                    'BSTAR': bstar,
                    'ephemeris': ephemeris,
                    'Element Set Number': setnum
                    },
            'Keplerian Elements': {
                    'inclination': i,
                    'RAAN': om,
                    'eccentricity': e,
                    'Argument Perigee': w,
                    'Mean Anomaly': M,
                    'Mean Motion': n,
                    'Rev #': rev_num
                    }
                }
            
    def __repr__(self):
        return "TLE(sat, line1, line2)"
    
    def __str__(self):
        out = "{\n"
        out += "    'info': {\n"
        for k, v in self.__data['info'].items():
            out += "        '{k}': {v}\n".format(k=k,v=v)
        out += "    }\n\n"
        out += "    'Keplerian Elements': {\n"
        for k, v in self.__data['Keplerian Elements'].items():
            out += "        '{k}': {v}\n".format(k=k,v=v)
        out += "    }\n"
        out += "}\n"
        
        return out
    
    def propagate(self, timestamp):
        if type(timestamp) != pd.Timestamp:
            raise TypeError("timestamp must be a pandas Timestamp datatype!")
        
        return None

class RedownloadFileError(Exception):
    pass

class SatelliteNotFoundException(Exception):
    pass

class SatelliteArray:
    def __init__(self, filename='active.txt'):
        self.__sats = dict()
        tles = []

        try:
            if time.time() - os.stat(filename)[stat.ST_MTIME] < 86400:
                with open(filename, 'r') as f:
                    tles = f.readlines()
        except (FileNotFoundError, RedownloadFileError):
            url = "http://celestrak.com/NORAD/elements/" + filename
            urllib.request.urlretrieve(url, filename)
            
            with open(filename, 'r') as f:
                    tles = f.readlines()
            
        for cnt in range(0, len(tles), 3):
            sat, line1, line2 = tles[cnt].strip(), tles[cnt+1].strip(), tles[cnt+2].strip()
            self.__sats[sat] = TLE(sat, line1, line2)
    
    def __repr__(self):
        return "SatelliteArray(filename='active.txt')"
    
    def get(self, sat):
        if sat in self.__sats.keys():
            return self.__sats[sat]
        else:
            raise SatelliteNotFoundException

birds = SatelliteArray()
print(birds.get("ISS (ZARYA)"))