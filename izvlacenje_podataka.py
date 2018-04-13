# -*- coding: utf-8 -*-
"""
Created on Tue May  9 17:28:46 2017

@author: luka
"""

import pandas as pd
import datetime
import numpy as np
import h5py
import random

def get_points(personx, persony, person_angle):
    points=np.empty([4,2])
    
    points[0,0]=personx+4000
    points[0,1]=persony+2500
    
    points[1,0]=personx-1000
    points[1,1]=persony+2500
    
    points[2,0]=personx-1000
    points[2,1]=persony-2500
    
    points[3,0]=personx+4000
    points[3,1]=persony-2500
    
    for i in range(0, 4):
        tempx=points[i,0]-personx
        tempy=points[i,1]-persony
        rotatedx=tempx*np.cos(person_angle)-tempy*np.sin(person_angle)
        rotatedy=tempx*np.sin(person_angle)+tempy*np.cos(person_angle)
        points[i,0]=rotatedx+personx
        points[i,1]=rotatedy+persony
    
    return points

    
def get_relative_points(person_angle):
    relative_points=np.empty([4,2])
    
    relative_points[0,0]=4000
    relative_points[0,1]=2500
    
    relative_points[1,0]=-1000
    relative_points[1,1]=2500
    
    relative_points[2,0]=-1000
    relative_points[2,1]=-2500
    
    relative_points[3,0]=4000
    relative_points[3,1]=-2500
    
    for i in range(0, 4):
        tempx=relative_points[i,0]
        tempy=relative_points[i,1]
        rotatedx=tempx*np.cos(person_angle)-tempy*np.sin(person_angle)
        rotatedy=tempx*np.sin(person_angle)+tempy*np.cos(person_angle)
        relative_points[i,0]=rotatedx
        relative_points[i,1]=rotatedy
        
    return relative_points

    
def rotate_around_origin(originx, originy, pointx, pointy, angle):
    rotatedx=originx+np.cos(angle)*(pointx-originx)-np.sin(angle)*(pointy-originy)
    rotatedy=originy+np.sin(angle)*(pointx-originx)+np.cos(angle)*(pointy-originy)
    
    return rotatedx, rotatedy

        
def is_inside(x, y, poly):
    n=len(poly)
    inside=False

    p1x, p1y=poly[0]
    for i in range(n+1):
        p2x,p2y = poly[i % n]
        if y > min(p1y,p2y):
            if y <= max(p1y,p2y):
                if x <= max(p1x,p2x):
                    if p1y != p2y:
                        xinters = (y-p1y)*(p2x-p1x)/(p2y-p1y)+p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x,p1y = p2x,p2y

    return inside



database=pd.read_csv('person_DIAMOR-1_all.csv', delimiter=',').values
print database[0,:]

persons_count=input('Nad koliko osoba zelite vrsiti test? ')
persons_ids=np.zeros(persons_count)
for i in range(0, persons_count):
    #persons_ids[i]=input('Unesite id zeljene osobe: ')
    persons_ids[i]=database[random.randint(0, database.shape[0]),1]
print persons_ids


numberof_records=0
for i in range(0, database.shape[0]):
    if database[i,1] in persons_ids and database[i,5]>400 and database[i,2]>=30000:
        numberof_records=numberof_records+1


numberof_iterations=0
is_left=False
ins=np.zeros((numberof_records, 2, 50, 50))
outs1s=np.zeros((numberof_records, 2))
outs2s=np.zeros((numberof_records, 2))
outs3s=np.zeros((numberof_records, 2))
outs4s=np.zeros((numberof_records, 2))
outs5s=np.zeros((numberof_records, 2))
central_row, central_column=39, 25

for i in range(0, database.shape[0]):
    if database[i,1] in persons_ids and database[i,5]>400 and database[i,2]>=30000:
        current_person=database[i,1]
        start_time=database[i,0]
        time=datetime.datetime.utcfromtimestamp(database[i,0]).strftime('%Y-%m-%d %H:%M:%S')
        print "U trenutku ", time, " pozicija je ", database[i,2], "x, ", database[i,3], "y"
        personx, persony, person_angle=database[i,2], database[i,3], database[i,6]
        if person_angle<0:
            person_angle=2*np.pi-abs(person_angle)
            
        if person_angle>np.pi/2 and person_angle<=(3*np.pi)/2:
            polygon=get_points(personx, persony, np.pi)
            is_left=True
        else:
            polygon=get_points(personx, persony, 0)
        #polygon_centered=get_relative_points(np.pi/2)
        
        
        if i+5000>database.shape[0]:
            for j in range(i-5000, database.shape[0]):
                if is_inside(database[j,2], database[j,3], polygon) and database[i,0]==database[j,0] and database[i,1]!=database[j,1]:
                    guestx=database[j,2]-personx
                    guesty=database[j,3]-persony
                    if is_left:
                        guestx=guestx*-1
                        guesty=guesty*-1
                    print "U blizini je id ", database[j,1], " rel. polozaj ", guestx, "x, ", guesty*-1, "y, brzine ", database [j,5], "mm/s, smjer kretanja ", database[j,6], " rad"
                    try:
                        ins[numberof_iterations,0,int(central_row-round(guestx/100)),int(central_column-round(guesty/100))]=database[j,5]/1000
                        ins[numberof_iterations,1,int(central_row-round(guestx/100)),int(central_column-round(guesty/100))]=database[j,6]
                    except:
                        print "Index ne moze biti 50!"
        else:
            for j in range(i-5000, i+5000):
                if is_inside(database[j,2], database[j,3], polygon) and database[i,0]==database[j,0] and database[i,1]!=database[j,1]:
                    guestx=database[j,2]-personx
                    guesty=database[j,3]-persony
                    if is_left:
                        guestx=guestx*-1
                        guesty=guesty*-1
                    print "U blizini je id ", database[j,1], " rel. polozaj ", guestx, "x, ", guesty, "y, brzine ", database [j,5], "mm/s, smjer kretanja ", database[j,6], " rad"
                    try:
                        ins[numberof_iterations,0,int(central_row-round(guestx/100)),int(central_column-round(guesty/100))]=database[j,5]/1000
                        ins[numberof_iterations,1,int(central_row-round(guestx/100)),int(central_column-round(guesty/100))]=database[j,6]
                    except:
                        print "Index ne moze biti 50!"
                
        ins[numberof_iterations,0,central_row,central_column]=database[i,5]/1000
        ins[numberof_iterations,1,central_row,central_column]=database[i,6]
        
        speed_cumulative, numberof_iterationsj=0, 0
        if i+10000>database.shape[0]:
            for j in range(i, database.shape[0]):
                if database[j,1]==current_person:
                    speed_cumulative=speed_cumulative+database[j,5]
                    numberof_iterationsj=numberof_iterationsj+1
                    if start_time+1>=database[j,0]:
                        if is_left:
                            outs1s[numberof_iterations,0]=((database[j,2]-personx)*-1)/1000
                            outs1s[numberof_iterations,1]=((database[j,3]-persony)*-1)/1000
                        else:
                            outs1s[numberof_iterations,0]=(database[j,2]-personx)/1000
                            outs1s[numberof_iterations,1]=(database[j,3]-persony)/1000
                    elif start_time+2>=database[j,0]:
                        if is_left:
                            outs2s[numberof_iterations,0]=((database[j,2]-personx)*-1)/1000
                            outs2s[numberof_iterations,1]=((database[j,3]-persony)*-1)/1000
                        else:
                            outs2s[numberof_iterations,0]=(database[j,2]-personx)/1000
                            outs2s[numberof_iterations,1]=(database[j,3]-persony)/1000
                        #print "Srednja brzina nakon 2 sekunde je: ", speed_cumulative/numberof_iterationsj, " mm/s"
                    elif start_time+3>=database[j,0]:
                        if is_left:
                            outs3s[numberof_iterations,0]=((database[j,2]-personx)*-1)/1000
                            outs3s[numberof_iterations,1]=((database[j,3]-persony)*-1)/1000
                        else:
                            outs3s[numberof_iterations,0]=(database[j,2]-personx)/1000
                            outs3s[numberof_iterations,1]=(database[j,3]-persony)/1000
                    elif start_time+4>=database[j,0]:
                        if is_left:
                            outs4s[numberof_iterations,0]=((database[j,2]-personx)*-1)/1000
                            outs4s[numberof_iterations,1]=((database[j,3]-persony)*-1)/1000
                        else:
                            outs4s[numberof_iterations,0]=(database[j,2]-personx)/1000
                            outs4s[numberof_iterations,1]=(database[j,3]-persony)/1000
                    elif start_time+5>=database[j,0]:
                        if is_left:
                            outs5s[numberof_iterations,0]=((database[j,2]-personx)*-1)/1000
                            outs5s[numberof_iterations,1]=((database[j,3]-persony)*-1)/1000
                        else:
                            outs5s[numberof_iterations,0]=(database[j,2]-personx)/1000
                            outs5s[numberof_iterations,1]=(database[j,3]-persony)/1000
                        #print "Srednja brzina nakon 5 sekundi je: ", speed_cumulative/numberof_iterationsj, " mm/s"
        else:
            for j in range(i, i+10000):
                if database[j,1]==current_person:
                    speed_cumulative=speed_cumulative+database[j,5]
                    numberof_iterationsj=numberof_iterationsj+1
                    if start_time+1>=database[j,0]:
                        if is_left:
                            outs1s[numberof_iterations,0]=((database[j,2]-personx)*-1)/1000
                            outs1s[numberof_iterations,1]=((database[j,3]-persony)*-1)/1000
                        else:
                            outs1s[numberof_iterations,0]=(database[j,2]-personx)/1000
                            outs1s[numberof_iterations,1]=(database[j,3]-persony)/1000
                    elif start_time+2>=database[j,0]:
                        if is_left:
                            outs2s[numberof_iterations,0]=((database[j,2]-personx)*-1)/1000
                            outs2s[numberof_iterations,1]=((database[j,3]-persony)*-1)/1000
                        else:
                            outs2s[numberof_iterations,0]=(database[j,2]-personx)/1000
                            outs2s[numberof_iterations,1]=(database[j,3]-persony)/1000
                        #print "Srednja brzina nakon 2 sekunde je: ", speed_cumulative/numberof_iterationsj, " mm/s"
                    elif start_time+3>=database[j,0]:
                        if is_left:
                            outs3s[numberof_iterations,0]=((database[j,2]-personx)*-1)/1000
                            outs3s[numberof_iterations,1]=((database[j,3]-persony)*-1)/1000
                        else:
                            outs3s[numberof_iterations,0]=(database[j,2]-personx)/1000
                            outs3s[numberof_iterations,1]=(database[j,3]-persony)/1000
                    elif start_time+4>=database[j,0]:
                        if is_left:
                            outs4s[numberof_iterations,0]=((database[j,2]-personx)*-1)/1000
                            outs4s[numberof_iterations,1]=((database[j,3]-persony)*-1)/1000
                        else:
                            outs4s[numberof_iterations,0]=(database[j,2]-personx)/1000
                            outs4s[numberof_iterations,1]=(database[j,3]-persony)/1000
                    elif start_time+5>=database[j,0]:
                        if is_left:
                            outs5s[numberof_iterations,0]=((database[j,2]-personx)*-1)/1000
                            outs5s[numberof_iterations,1]=((database[j,3]-persony)*-1)/1000
                        else:
                            outs5s[numberof_iterations,0]=(database[j,2]-personx)/1000
                            outs5s[numberof_iterations,1]=(database[j,3]-persony)/1000
                        #print "Srednja brzina nakon 5 sekundi je: ", speed_cumulative/numberof_iterationsj, " mm/s"
        
        outs1s[numberof_iterations,0], outs1s[numberof_iterations,1]=rotate_around_origin(0, 0, outs1s[numberof_iterations,0], outs1s[numberof_iterations,1], np.pi/2)
        outs2s[numberof_iterations,0], outs2s[numberof_iterations,1]=rotate_around_origin(0, 0, outs2s[numberof_iterations,0], outs2s[numberof_iterations,1], np.pi/2)
        outs3s[numberof_iterations,0], outs3s[numberof_iterations,1]=rotate_around_origin(0, 0, outs3s[numberof_iterations,0], outs3s[numberof_iterations,1], np.pi/2)
        outs4s[numberof_iterations,0], outs4s[numberof_iterations,1]=rotate_around_origin(0, 0, outs4s[numberof_iterations,0], outs4s[numberof_iterations,1], np.pi/2)
        outs5s[numberof_iterations,0], outs5s[numberof_iterations,1]=rotate_around_origin(0, 0, outs5s[numberof_iterations,0], outs5s[numberof_iterations,1], np.pi/2)
        #print "Nakon 1 s rel polozaj: ", outs1s[numberof_iterations,0],"x, ", outs1s[numberof_iterations,1], "y"
        #print "Nakon 2 s rel polozaj: ", outs2s[numberof_iterations,0],"x, ", outs2s[numberof_iterations,1], "y"
        #print "Nakon 3 s rel polozaj: ", outs3s[numberof_iterations,0],"x, ", outs3s[numberof_iterations,1], "y"
        #print "Nakon 4 s rel polozaj: ", outs4s[numberof_iterations,0],"x, ", outs4s[numberof_iterations,1], "y"
        #print "Nakon 5 s rel polozaj: ", outs5s[numberof_iterations,0],"x, ", outs5s[numberof_iterations,1], "y"
        
        numberof_iterations=numberof_iterations+1
        is_left=False



for_deletion=np.argwhere(np.sqrt(np.square(outs5s[:,0])+np.square(outs5s[:,1]))<1)
outs5s=np.delete(outs5s, for_deletion, 0)
ins=np.delete(ins, for_deletion, 0)

for_deletion=np.argwhere(outs5s[:,1]<0)
outs5s=np.delete(outs5s, for_deletion, 0)
ins=np.delete(ins, for_deletion, 0)

index=np.argwhere(np.abs(np.arctan2(outs5s[:,0], outs5s[:,1]))<0.1)
index2=np.argwhere(np.abs(np.arctan2(outs5s[:,0], outs5s[:,1]))>0.1)
for_deletion=index[0:int(index.shape[0]-round(index2.shape[0]/0.7-index2.shape[0])),:]
outs5s=np.delete(outs5s, for_deletion, 0)
ins=np.delete(ins, for_deletion, 0)

h5fw=h5py.File('insouts.h5', 'w')
h5fw.create_dataset("ins", data=ins, compression='lzf')
h5fw.create_dataset("outs", data=outs5s, compression='lzf')
h5fw.close()