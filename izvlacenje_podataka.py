# -*- coding: utf-8 -*-
"""
Created on Tue May  9 17:28:46 2017

@author: luka
"""

import pandas as pd
import numpy as np
import h5py
import random
import sys

def progress_bar(count, total, status=''):
    bar_len=40
    filled_len=int(round(bar_len*count/float(total)))
    
    percents=round(100.0*count/float(total), 1)
    bar='='*filled_len+'-'*(bar_len-filled_len)
    
    sys.stdout.write('\r[%s] %s%s %s\r' % (bar, percents, '%', status))
    sys.stdout.flush()

database=pd.read_csv('person_DIAMOR-1_all.csv', delimiter=',').values
print "Database loaded."

persons_count=input('From how many pedestrians would you like to extract data? ')
persons_ids=np.zeros(persons_count)
for i in range(0, persons_count):
    #persons_ids[i]=input('Unesite id zeljene osobe: ')
    persons_ids[i]=database[random.randint(0, database.shape[0]),1]

records=database[(database[:,1]==persons_ids[0]) & (database[:,5]>400) & (database[:,2]>=30000),:]
for i in range(1, persons_count):
    records=np.vstack((records, database[(database[:,1]==persons_ids[i]) & (database[:,5]>400) & (database[:,2]>=30000),:]))
numberof_records=records.shape[0]
print "Records loaded."

ins=np.zeros((numberof_records, 2, 50, 50))
outs=np.zeros((numberof_records, 2))
for_deletion=[]
central_row, central_column=39, 25
seconds_after=5

for i in range(0, numberof_records):
    progress_bar(i, numberof_records, status='Extracting data...')
    is_left=False
    start_time, person_id, personx, persony, person_velocity, person_angle=records[i,0], records[i,1], records[i,2], records[i,3], records[i,5], records[i,6]
    if person_angle<0:
        person_angle=2*np.pi-abs(person_angle)
    if person_angle>np.pi/2 and person_angle<=(3*np.pi)/2:
        is_left=True
        
    dbt=database[(database[:,0]==start_time),:]
    if is_left:
        guests=dbt[(dbt[:,1]<>person_id) & ((dbt[:,2]-personx)<1000) & ((dbt[:,2]-personx)>-5000) & (abs(dbt[:,3]-persony)<2500),:]
    else:
        guests=dbt[(dbt[:,1]<>person_id) & ((dbt[:,2]-personx)<5000) & ((dbt[:,2]-personx)>-1000) & (abs(dbt[:,3]-persony)<2500),:]
    for j in range(0, guests.shape[0]):
        guestx, guesty, guest_angle=guests[j,2], guests[j,3], guests[j,6]
        if guest_angle<0:
            guest_angle=2*np.pi-abs(guest_angle)
        
        guestx=personx-guestx
        guesty=persony-guesty
        if is_left:
            guesty=guesty*-1
        else:
            guestx=guestx*-1
        try:
            ins[i,0,int(central_row-(guestx/100)),int(central_column+(guesty/100))]=guests[j,5]/1000
            ins[i,1,int(central_row-(guestx/100)),int(central_column+(guesty/100))]=guest_angle
        except:
            print "Index can't be larger than 50!"
    ins[i,0,central_row,central_column]=person_velocity/1000
    ins[i,1,central_row,central_column]=person_angle
    
    person_after=database[(database[:,1]==person_id) & (database[:,0]<=start_time+seconds_after) & (database[:,0]>start_time),:]
    if not person_after.any():
        for_deletion.append(i)
        continue
    outs[i,0]=personx-person_after[-1,2]
    outs[i,1]=persony-person_after[-1,3]
    if is_left:
        outs[i,1]=outs[i,1]*-1
    else:
        outs[i,0]=outs[i,0]*-1
    outs[i,0]=outs[i,0]/100
    outs[i,1]=outs[i,1]/100
    
outs=np.delete(outs, for_deletion, 0)
ins=np.delete(ins, for_deletion, 0)
'''
#delete everyone that moved less than 1m        
for_deletion=np.argwhere(np.sqrt(np.square(outs[:,0])+np.square(outs[:,1]))<1)
outs=np.delete(outs, for_deletion, 0)
ins=np.delete(ins, for_deletion, 0)

#delete everyone that moved backwards
for_deletion=np.argwhere(outs[:,0]<0)
outs=np.delete(outs, for_deletion, 0)
ins=np.delete(ins, for_deletion, 0)

index=np.argwhere(np.abs(np.arctan2(outs[:,0], outs[:,1]))<0.1)
index2=np.argwhere(np.abs(np.arctan2(outs[:,0], outs[:,1]))>0.1)
for_deletion=index[0:int(index.shape[0]-round(index2.shape[0]/0.7-index2.shape[0])),:]
outs=np.delete(outs, for_deletion, 0)
ins=np.delete(ins, for_deletion, 0)
'''
h5fw=h5py.File('insouts.h5', 'w')
h5fw.create_dataset("ins", data=ins, compression='lzf')
h5fw.create_dataset("outs", data=outs, compression='lzf')
h5fw.close()
print "Done."