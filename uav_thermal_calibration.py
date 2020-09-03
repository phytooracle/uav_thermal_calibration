#!/usr/bin/env python3
"""
Author : Emmanuel Gonzalez
Date   : 2020-08-10
Purpose: Calibrate UAV thermal images
"""

import argparse
import os
import sys
import numpy as np
import pandas as pd
import numpy as np
from osgeo import gdal, osr
from terrautils.formats import create_geotiff
from PIL import Image
import glob
import exifread
import piexif
from GPSPhoto import gpsphoto
import subprocess


# --------------------------------------------------
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='Calibrate UAV thermal images',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('dir',
                        metavar='str',
                        help='Input directory with raw TIFs')

    parser.add_argument('-o',
                        '--outdir',
                        help='Output directory',
                        metavar='str',
                        type=str,
                        default='uav_tif_calibration')

    args = parser.parse_args()

    if '/' not in args.dir:
        args.dir = args.dir + '/'

    return args


# --------------------------------------------------
def raw2temp(array, meta_df):

    T = meta_df['TempFPA'][0]

    P_5_outmean = [-2.634587235100472e-09,
                    6.130769700215367e-05,
                    -4.350477995778048e-01,
                    9.544260005306576e+02]


    P_15_outmean = [-6.018041990346753e-09,
                    1.403164304077759e-04,
                    -1.049703754495839e+00,
                    2.547437846222635e+03]


    P_20_outmean = [-2.671172491930611e-09,
                    6.241064309639934e-05,
                    -4.484195421602772e-01,
                    1.010144114109549e+03]


    P_25_outmean = [-1.983581717393769e-09,
                    4.279525635707080e-05,
                    -2.680343341771736e-01,
                    4.699920069946522e+02]


    P_30_outmean = [-3.859617072855032e-09,
                    8.898414965915169e-05,
                    -6.459860053057492e-01,
                    1.498378686527253e+03]


    P_35_outmean = [2.795686755385618e-09,
                    -6.118221864082072e-05,
                    4.820433347884710e-01,
                    -1.322798944546627e+03]


    P_40_outmean = [-4.531711796485001e-09,
                    1.048040213336373e-04,
                    -7.693362093422826e-01,
                    1.817901230928576e+03]


    P_45_outmean = [-5.488794161933038e-09,
                    1.265335698783423e-04,
                    -9.331169837051072e-01,
                    2.228396565151564e+03]

    T_list = [5, 15, 20, 25, 30, 35, 40, 45]

    a = [P_5_outmean[0], P_15_outmean[0], P_20_outmean[0],
         P_25_outmean[0], P_30_outmean[0], P_35_outmean[0],
         P_40_outmean[0], P_45_outmean[0]]
    b = [P_5_outmean[1], P_15_outmean[1], P_20_outmean[1],
         P_25_outmean[1], P_30_outmean[1], P_35_outmean[1],
         P_40_outmean[1], P_45_outmean[1]]
    c = [P_5_outmean[2], P_15_outmean[2], P_20_outmean[2],
         P_25_outmean[2], P_30_outmean[2], P_35_outmean[2],
         P_40_outmean[2], P_45_outmean[2]]
    d = [P_5_outmean[3], P_15_outmean[3], P_20_outmean[3],
         P_25_outmean[3], P_30_outmean[3], P_35_outmean[3],
         P_40_outmean[3], P_45_outmean[3]]

    P_val = [np.interp(T, T_list, a), np.interp(T, T_list, b),
                       np.interp(T, T_list, c), np.interp(T, T_list, d)]

    im = array

    pxl_temp = P_val[0]*im**3 + P_val[1]*im**2 + P_val[2]*im + P_val[3]

    return pxl_temp


# --------------------------------------------------
def main():
    """Calibrate images here"""
    args = get_args()
    img_list = glob.glob(f'{args.dir}/*.tif', recursive=True)
    out_path = args.outdir

    if not os.path.isdir(out_path):
        os.makedirs(out_path)

    for img in img_list:

        meta_path = img.replace('.tif', '_meta.csv')
        filename = os.path.basename(img)
        outfile = os.path.join(os.getcwd(), out_path, filename)
        print(outfile)

        meta_df = pd.read_csv(meta_path, delimiter=';')
        print(meta_df['TempFPA'][0])

        g_img = gdal.Open(img)
        exif_dict = piexif.load(img)
        zeroth = str(exif_dict['0th'])
        exif = str(exif_dict['Exif'])
        GPS = str(exif_dict['GPS'])

        gps_data = gpsphoto.getGPSData(img)
        rawData = gpsphoto.getRawData(img)

        raw_data = g_img.GetRasterBand(1).ReadAsArray().astype('float')
        tc = raw2temp(raw_data, meta_df)

        create_geotiff(tc, (0, 0, 0, 0), outfile, None, True, None,
            extra_metadata=[
                f'0th={str(zeroth.strip("{}"))}\n\
                Exif={str(exif.strip("{}"))}\n\
                GPS={str(GPS.strip("{}"))}\n'
            ], compress=False)

        cmd = f'exiftool -overwrite_original -TagsFromFile {img} {outfile}'
        subprocess.call(cmd, shell=True)

        exif_dict = piexif.load(outfile)
        gps_data = gpsphoto.getGPSData(outfile)
        print(f'{gps_data}\n')


# --------------------------------------------------
if __name__ == '__main__':
    main()