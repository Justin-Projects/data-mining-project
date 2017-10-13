import argparse
import numpy as np
import os
import math
import json
import pandas as pd
import datetime


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("data", help= "Data to be processed")
    parser.add_argument("output", help="Output directory")
    parser.add_argument("-f","--file",help="Specify a single file to process", action="store_true" )
    parser.add_argument("-d","--directory", help="Specify a directory of files to process", action="store_true")
    parser.add_argument("--convert", help="Take input data in JSON format and convert into csv", action="store_true")
    parser.add_argument("--extract", help="Take input data and extract important features", action="store_true")
    parser.add_argument("--transform", help="Take input data and convert Latitude, Longitude and Altitude to X,Y,Z", action="store_true")
    parser.add_argument("-o","--output", help = "Specify output file path")
    args = parser.parse_args()
    
    sim_time = datetime.datetime.now().strftime('%H_%M_%S')
    
    if args.file:
        data_file = args.data
        output_file = os.path.join(args.output,sim_time+"_converted.csv")
        
        print("PROCESSING FILE--> ", data_file)
        print("Outputting to -->", output_file)
        
        if args.convert:
            print("Converting file")
            raw_adsb = import_adsb_file(data_file)
            export_raw_adsb(output_file,  raw_adsb)
            
        if args.extract:
            adsb_csv = pd.read_csv(data_file)
            export_transformed_adsb(output_file, "test_file.csv")
        
    elif args.directory:
        data_directory = args.data
        output_directory= args.output
        
        for root, directories,filenames in os.walk(data_directory):
            
            for filename in filenames:
                file_to_process = os.path.join(root, filename)
                print("PROCESSING FILE--> ", file_to_process)
                
                if args.convert:
                    raw_adsb = import_adsb_file(file_to_process)
                    export_raw_adsb(output_directory+"\\"+sim_time+"_converted", raw_adsb )
                    
                if args.extract:
                    adsb_csv = pd.read_csv(file_to_process)
                    export_transformed_adsb(output_directory+"\\"+sim_time+"_converted", adsb_csv)
                
                
def import_adsb_file(filename):
    with open(filename, encoding="utf8") as data_file:
        data = json.load(data_file)
        
    return data
    

def export_raw_adsb(filename, data):
    adsb_data = pd.DataFrame(data["acList"])
    
    adsb_data.to_csv(path_or_buf=filename, na_rep="na", mode="a")
     
def export_transformed_adsb(filename, data):
    
    #Check if aircraft is in flight
    #Check if there are any COS values
    #Extract important features with low sparsity
    #Not biased to aircraft type. One could argue larger planes can withstand a stronger hit from UAV
    #Heading two sparced
    #Filter if grounded, if not available 
    
    resultant_set = []
    for ac in data["acList"]:
        
        global STATS_TOTAL_RECORDS
        global STATS_FILTERED_RECORDS
        global STATS_NO_COS_FOUND
        global STATS_GND_STATE_UNKNOWN
        
        STATS_TOTAL_RECORDS = STATS_TOTAL_RECORDS + 1
        try:
            #aircraft_grounded = ac['Gnd']
            
            if ac['Gnd'] == False:
                
                
                i=0
                try:
                    cos_values = ac["Cos"]
                    latitude = cos_values[i]
                    longitude = cos_values[i+1]
                    timestamp = cos_values[i+2]
                    altitude = cos_values[i+3]
                    
                    engine_type = ac["EngType"]
                
                    while i < len(cos_values):
                        resultant_set.append({"Latitude":latitude, "Longitude":longitude, "TimeStamp": timestamp, "Altitude":altitude, "EngineType":engine_type})
                        STATS_FILTERED_RECORDS = STATS_FILTERED_RECORDS + 1
                        i = i+4
                except KeyError:
                    i=i+4
                    STATS_NO_COS_FOUND = STATS_NO_COS_FOUND+1
                    
        except KeyError:
            STATS_GND_STATE_UNKNOWN = STATS_GND_STATE_UNKNOWN + 1
        

    transformed = pd.DataFrame(resultant_set)
    
    transformed.to_csv(path_or_buf=filename, na_rep="na", mode="a" )
    
    return transformed
    
def lla_to_ecef_1(lat, lon, alt):
    # see http://www.mathworks.de/help/toolbox/aeroblks/llatoecefposition.html
    rad = np.float64(6378137.0)        # Radius of the Earth (in meters)
    f = np.float64(1.0/298.257223563)  # Flattening factor WGS84 Model
    cosLat = np.cos(lat)
    sinLat = np.sin(lat)
    FF     = (1.0-f)**2
    C      = 1/np.sqrt(cosLat**2 + FF * sinLat**2)
    S      = C * FF

    x = (rad * C + alt)*cosLat * np.cos(lon)
    y = (rad * C + alt)*cosLat * np.sin(lon)
    z = (rad * S + alt)*sinLat
    return x, y, z

#WGS84 ellipsoid constants
def convert_ecef_to_geodetic(x,y,z):
    a = 6378137
    b = 6.3568 * math.exp(6)
    f = 0.0034
    
    e = math.sqrt((math.pow(a,2) - math.pow(b,2))/ math.pow(a,2))
    e2 = math.sqrt((math.pow(a,2) - math.pow(b,2))/math.pow(b,2))
    
    p = math.sqrt(math.pow(x,2) + math.pow(y,2))
    theta = math.atan((z * a) / (p*b))
    lon = math.atan(y/x)
    lat = math.atan(((z + math.pow(e2, 2) * b * math.pow(math.sin(theta), 3)) / ((p - math.pow(e, 2) * a * math.pow(math.cos(theta), 3)))))
    N = a / (math.sqrt(1 - (math.pow(e, 2) * math.pow(math.sin(lat), 2))))
    
    m = (p/math.cos(lat))
    height = m-N
    
    lon = lon * 180 / math.pi;
    lat = lat * 180 / math.pi; 
    
    return (lat, lon, height)           

main()
    

