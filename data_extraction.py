# -*- coding: utf-8 -*-
"""
Created on Tue May  9 17:28:46 2017

@author: luka
"""

import pandas as pd
import numpy as np
import h5py
import sys

def progress_bar(count, total, status=''):
    bar_len=40
    filled_len=(bar_len*count)/total
    
    percents=100.0*count/float(total)
    bar='='*filled_len+'-'*(bar_len-filled_len)
    
    sys.stdout.write('\r[%s] %3.1f%s %s\r' % (bar, percents, '%', status))
    sys.stdout.flush()

#@profile
def calculate_all():

    # ucitaj podatke (CSV)
    #database=pd.read_csv('data/person_DIAMOR-1_all.csv', delimiter=',').values
    #database=database[(database[:,5]>400) & (database[:,2]>=30000),:]
    
    # snimi u h5
    #h5fw=h5py.File('data/person_DIAMOR-1_all.h5', 'w')
    #insds  = h5fw.create_dataset("data", data=database, compression='lzf')
    #h5fw.close()
    #return
    
    # ucitaj iz h5 - puno brze od CSV
    h5fw=h5py.File('data/person_DIAMOR-1_all_recalculated.h5', 'r')
    database = h5fw['data'][:]
    h5fw.close()
    
    dbsize = database.shape[0]
    
    print "Database loaded (size = %d)." % (dbsize)

    
    persons_count=input('From how many pedestrians would you like to extract data? ')
    #persons_count=50
    
    if (persons_count == 0):
        return
    
    if (persons_count < 0):
        # svi id
        persons_ids = np.unique(database[:,1])
        persons_count = persons_ids.shape[0]
    else:
        # odabir id bez ponavljanja
        persons_ids=database[np.random.choice(database.shape[0], persons_count, replace=False),1]

    # arrays (buffers) for saving output data
    arrsize = 10000
    ins=np.zeros((arrsize, 2, 20, 20))
    outs=np.zeros((arrsize, 2))
    
    # h5 output file and datasets
    h5fw=h5py.File('data/neural_network_insouts.h5', 'w')
    insds  = h5fw.create_dataset("ins",  (0, 2, 20, 20), maxshape=(None, 2, 20, 20), compression='lzf')
    outsds = h5fw.create_dataset("outs", (0, 2), maxshape=(None, 2), compression='lzf')
    
    # brojac
    cnt = 0;
        
    for k in range(0, persons_count):
        
        progress_bar(k, persons_count, status='Extracting data...')

        person_id = persons_ids[k]
        
        # zapisi s person_id
        i_dbtpers = np.where(database[:,1]==person_id)[0]
        
        # svaki n-ti uzorak (ionako su bliski uzorci vrlo slicni)
        i_dbtpers=i_dbtpers[::2]

        dbtpers=database[i_dbtpers,:]

        numberof_records=dbtpers.shape[0]

        central_row, central_column=16, 10
        seconds_after = 2 #5
        #seconds_before = 2  za izgladjivanje brzine (napravljeno izravno u bazi)

        
        for i in range(0, numberof_records):

            is_left=False
            start_time, personx, persony, person_velocity, person_angle=dbtpers[i,0], dbtpers[i,2], dbtpers[i,3], dbtpers[i,5], dbtpers[i,6]
            
            # zapis za istu osobu prije seconds_before sekundi
            #person_before=dbtpers[(dbtpers[:,0]<=start_time-seconds_before) & (dbtpers[:,0]>start_time-seconds_before-0.1),:]
            #if not person_before.any():
            #    continue
                
            #dx_before = person_before[-1,2]-personx
            #dy_before = person_before[-1,3]-persony
            
            # izracunaj izgladjene vrijednosti brzine i kuta
            #person_velocity_calc = np.sqrt(dx_before*dx_before+dy_before*dy_before) / seconds_before;
            #person_angle_calc = np.arctan2(dy_before, dx_before);
            
            # prespori - ne hodaju
            if person_velocity < 500:
                continue
            
            # prevelik kut - ne idu uzduz hodnika / imaju drugaciji cilj
            #if np.abs(person_angle_calc) > 0.25:  # krivo!
            #    continue
            
            if person_angle<0:
                person_angle=2*np.pi-abs(person_angle)
            # ne idu uzduz hodnika / imaju drugaciji cilj
            if (person_angle>0.2 and person_angle<np.pi-0.2) or (person_angle>np.pi+0.2 and person_angle<2*np.pi-0.2):
                continue
            if not (person_angle>np.pi/2 and person_angle<=(3*np.pi)/2):
                is_left=True
                
            
            # zapis za istu osobu poslije seconds_after sekundi
            person_after=dbtpers[(dbtpers[:,0]<=start_time+seconds_after) & (dbtpers[:,0]>start_time+seconds_after-0.1),:]
            if not person_after.any():
                continue
            
            # zapisi s istim vremenom su jedan do drugoga - traži samo bliske zapise (radi ubrzanja)
            start_at = np.max((i_dbtpers[i]-50,0))
            end_at = np.min((i_dbtpers[i]+50,dbsize))
            i_dbt = np.where(database[start_at:end_at,0]==start_time)[0]
            dbt=database[start_at+i_dbt,:]
            
            # za testiranje - podaci o najblizoj osobi
            #closestdist = 100000
            #closestang = 0
            #closestv = 0
            #closestvang = 0
            
            if is_left:
                guests=dbt[(dbt[:,1]<>person_id) & ((dbt[:,2]-personx)<1000) & ((dbt[:,2]-personx)>-5000) & (abs(dbt[:,3]-persony)<2500),:]
            else:
                guests=dbt[(dbt[:,1]<>person_id) & ((dbt[:,2]-personx)<5000) & ((dbt[:,2]-personx)>-1000) & (abs(dbt[:,3]-persony)<2500),:]
            for j in range(0, guests.shape[0]):
                guestx, guesty, guest_velocity, guest_angle=guests[j,2], guests[j,3], guests[j,5], guests[j,6]
                if guest_angle<0:
                    guest_angle=2*np.pi-abs(guest_angle)
                
                guestx=personx-guestx
                guesty=persony-guesty
                if is_left:
                    guesty=guesty*-1
                else:
                    guestx=guestx*-1
                v0x=person_velocity*np.cos(person_angle)
                v0y=person_velocity*np.sin(person_angle)
                v1x=guest_velocity*np.cos(guest_angle)
                v1y=guest_velocity*np.sin(guest_angle)
                dvx=v1x-v0x
                dvy=v1y-v0y
                dv=np.sqrt(np.square(dvx)+np.square(dvy))
                angle=np.arctan2(dvy, dvx)
                if angle<0:
                    angle=2*np.pi-abs(angle)
                try:
                    ins[cnt,0,int(central_row-(guestx/250)),int(central_column+(guesty/250))]=dv/1000
                    ins[cnt,1,int(central_row-(guestx/250)),int(central_column+(guesty/250))]=angle
                except:
                    print "Index can't be larger than 20!"
                
                #gdist = np.sqrt(guestx*guestx+guesty*guesty)
                #if closestdist > gdist:
                #    closestdist = gdist
                #    closestang = np.arctan2(guesty, guestx)
                #    closestv, closestvang = guests[j,5], guests[j,6]
            
            # ne uspisujemo podatke o promatranoj osobi
            #ins[cnt,0,central_row,central_column]=person_velocity/1000
            #ins[cnt,1,central_row,central_column]=person_angle
            
            outs[cnt,0]=personx-person_after[-1,2]
            outs[cnt,1]=persony-person_after[-1,3]
            if is_left:
                outs[cnt,1]=outs[cnt,1]*-1
            else:
                outs[cnt,0]=outs[cnt,0]*-1
            outs[cnt,0]=outs[cnt,0]/1000
            outs[cnt,1]=outs[cnt,1]/1000
            
            # za testiranje:
            # brzine i kutevi
            #outs[cnt,2]=person_velocity
            #outs[cnt,3]=person_angle
            #outs[cnt,4]=person_velocity_calc
            #outs[cnt,5]=person_angle_calc
            # najbliža okolna osoba
            #outs[cnt,6]=closestdist
            #outs[cnt,7]=closestang
            #outs[cnt,8]=closestv
            #outs[cnt,9]=closestvang
            
            
            cnt += 1
            
            # pun buffer - zapisivanje u h5 datoteku
            if cnt >= arrsize:
                insds.resize(insds.shape[0]+arrsize, axis=0)
                insds[-arrsize:] = ins
                outsds.resize(outsds.shape[0]+arrsize, axis=0)
                outsds[-arrsize:] = outs
                cnt = 0
        
        
    if cnt != 0:
        # zapisi preostale podatke
        ins=ins[:cnt,:,:,:]
        outs = outs[:cnt,:]
        
        insds.resize(insds.shape[0]+cnt, axis=0)
        insds[-cnt:] = ins
        outsds.resize(outsds.shape[0]+cnt, axis=0)
        outsds[-cnt:] = outs

    #delete everyone that moved less than XXm        
    #for_deletion=np.argwhere(np.sqrt(np.square(outs[:,0])+np.square(outs[:,1]))<1)
    #outs=np.delete(outs, for_deletion, 0)
    #ins=np.delete(ins, for_deletion, 0)

    #delete everyone that moved backwards
    #for_deletion=np.argwhere(outs[:,0]<0)
    #outs=np.delete(outs, for_deletion, 0)
    #ins=np.delete(ins, for_deletion, 0)
        
    #only in 30% of instances should the pedestrian move straight ahead without anyone impacting their movement
    #index=np.argwhere(np.abs(np.arctan2(outs[:,0], outs[:,1]))<0.1)
    #index2=np.argwhere(np.abs(np.arctan2(outs[:,0], outs[:,1]))>0.1)
    #for_deletion=index[0:int(index.shape[0]-round(index2.shape[0]/0.7-index2.shape[0])),:]
    #outs=np.delete(outs, for_deletion, 0)
    #ins=np.delete(ins, for_deletion, 0)

    h5fw.close()
    print "Done."


if __name__ == "__main__":
    calculate_all()

