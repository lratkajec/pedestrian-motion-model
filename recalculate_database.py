# -*- coding: utf-8 -*-
"""
Created on Sun May 13 15:22:24 2018

@author: luka
"""

import pandas as pd
import numpy as np
import sys
import h5py

def progress_bar(count, total, status=''):
    bar_len=40
    filled_len=(bar_len*count)/total
    
    percents=round(100.0*count/float(total), 1)
    bar='='*filled_len+'-'*(bar_len-filled_len)
    
    sys.stdout.write('\r[%s] %s%s %s\r' % (bar, percents, '%', status))
    sys.stdout.flush()

#@profile
def recalculate():    
    database=pd.read_csv('data/person_DIAMOR-1_all.csv', delimiter=',').values
    database=database[(database[:,5]>400) & (database[:,2]>=30000),:]
    dbsize = database.shape[0]
    print "Database loaded (size = %d)." % (dbsize)
    
    seconds_before=2
    to_write=np.zeros(database.shape)
    
    for i in range(0, dbsize):
        progress_bar(i, dbsize, status='Recalculating data...')    
        
        start_time, person_id, personx, persony=database[i,0], database[i,1], database[i,2], database[i,3]
        
        to_write[i]=database[i]
        
        db_close=database[i-500:i]
        # zapis za istu osobu prije seconds_before sekundi
        person_before=db_close[(db_close[:,1]==person_id) & (db_close[:,0]<=start_time-seconds_before) & (db_close[:,0]>start_time-seconds_before-0.1),:]
        if not person_before.any():
            continue
        else:
            dx_before = person_before[-1,2]-personx
            dy_before = person_before[-1,3]-persony
            person_velocity_calc = np.sqrt(dx_before*dx_before+dy_before*dy_before) / seconds_before;
            person_angle_calc = np.arctan2(dy_before, dx_before);
            to_write[i,5], to_write[i,6]=person_velocity_calc, person_angle_calc
            
    h5fw=h5py.File('data/person_DIAMOR-1_all_recalculated.h5', 'w')
    h5fw.create_dataset("data", data=to_write, compression='lzf')
    h5fw.close()
    
if __name__ == "__main__":
    recalculate()
