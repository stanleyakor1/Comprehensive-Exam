
#check if the path exists


import os
from datetime import datetime, timedelta
import pandas as pd
import sys
import urllib.request
import platform
import multiprocessing as mp
from download import *


'''

Download SNODAS data for a given range of datetime.
Akor Stanley, 07-16-2023

'''

def make_date_range(start_date, end_date):
    if type(start_date) == str:
        start_date = pd.to_datetime(start_date)
    if type(end_date) == str:
        end_date = pd.to_datetime(end_date)

    date_range = pd.date_range(start_date, end_date, freq='1D')
    return date_range

def make_url(date, masked=True):
    year = date.year
    month = date.strftime('%m')
    month_abbr = date.strftime('%b')
    day = date.strftime('%d')

    if masked:
        URLpath = f'https://noaadata.apps.nsidc.org/NOAA/G02158/masked/{year}/{month}_{month_abbr}/SNODAS_{year}{month}{day}.tar'
        filename = f'SNODAS_{year}{month}{day}.tar'
    else:
        URLpath = f'https://noaadata.apps.nsidc.org/NOAA/G02158/masked/{year}/{month}_{month_abbr}/SNODAS_unmasked_{year}{month}{day}.tar'
        filename = f'SNODAS_unmasked_{year}{month}{day}.tar'

    return URLpath, filename


def download_url(start_date, end_date, path='./SNODAS/', masked=True):
    date_range = make_date_range(start_date, end_date)
    file_names = []
    url_list = []
    

    for date in date_range:
        URLpath, filename = make_url(date, masked)
        file_names.append(filename)
        url_list.append(URLpath)

    return url_list, file_names


if __name__ == "__main__":
    start_date = '2023-01-01'
    end_date = '2023-01-02'
    path = 'SNODAS'
    masked = True
    unzip = True
    remove_compressed = True
    url_list, file_names = download_url(start_date, end_date, path, masked)


    #check if the path exists

    snodas_path = os.getcwd()
    snodas_path = os.path.join(snodas_path, path)

    if not os.path.exists(snodas_path):

        try:

            # create the directory if it doesn't exist
            os.makedirs(snodas_path)

            os.chdir(snodas_path)


            #Download the files into the directory
            print(f'Now downloading files!.........')
            with mp.Pool(processes=int(sys.argv[1])) as pool:
                results_async = pool.map(download_data, zip(url_list, file_names))

                pool.close()
                pool.join()

        except Exception as e:
            print(e)

    else:

        try:

            os.chdir(snodas_path)

            print(f'Now downloading files!.........')

            with mp.Pool(processes=int(sys.argv[1])) as pool:
                results_async = pool.map(download_data, zip(url_list, file_names))

                pool.close()
                pool.join()

        except Exception as e:
            print(e)

    if unzip:

        files_to_unzip = [filename for filename in os.listdir(snodas_path) if filename.endswith('.tar')]

        for file_unzip in files_to_unzip:

            try:
                untar_file(os.path.join(snodas_path, file_unzip), snodas_path)

            except Exception as e:
                print(f'Error unzipping file: {e}')


        try: 
            uncompress_all_gz_files(snodas_path)

        except Exception as e:
            print(f'Error gunzipping files .....')

    if remove_compressed:

        try: 
             remove_compressed_files(snodas_path)

        except Exception as e:

            print(f'Error deleting compressed files....')

    print('All Done!')
        
#hmdir = os.path.expanduser("~")
#snodas_path = os.path.join(hmdir, path)
