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

def getPoints(osobaX, osobaY, osobaKut):
    points=np.empty([4,2])
    
    points[0,0]=osobaX+4000
    points[0,1]=osobaY+2500
    
    points[1,0]=osobaX-1000
    points[1,1]=osobaY+2500
    
    points[2,0]=osobaX-1000
    points[2,1]=osobaY-2500
    
    points[3,0]=osobaX+4000
    points[3,1]=osobaY-2500
    
    for i in range(0, 4):
        tempX=points[i,0]-osobaX
        tempY=points[i,1]-osobaY
        rotatedX=tempX*np.cos(osobaKut)-tempY*np.sin(osobaKut)
        rotatedY=tempX*np.sin(osobaKut)+tempY*np.cos(osobaKut)
        points[i,0]=rotatedX+osobaX
        points[i,1]=rotatedY+osobaY
    
    return points

    
def getRelativePoints(osobaKut):
    relativePoints=np.empty([4,2])
    
    relativePoints[0,0]=4000
    relativePoints[0,1]=2500
    
    relativePoints[1,0]=-1000
    relativePoints[1,1]=2500
    
    relativePoints[2,0]=-1000
    relativePoints[2,1]=-2500
    
    relativePoints[3,0]=4000
    relativePoints[3,1]=-2500
    
    for i in range(0, 4):
        tempX=relativePoints[i,0]
        tempY=relativePoints[i,1]
        rotatedX=tempX*np.cos(osobaKut)-tempY*np.sin(osobaKut)
        rotatedY=tempX*np.sin(osobaKut)+tempY*np.cos(osobaKut)
        relativePoints[i,0]=rotatedX
        relativePoints[i,1]=rotatedY
        
    return relativePoints

    
def rotateAroundOrigin(originX, originY, pointX, pointY, angle):
    rotatedX=originX+np.cos(angle)*(pointX-originX)-np.sin(angle)*(pointY-originY)
    rotatedY=originY+np.sin(angle)*(pointX-originX)+np.cos(angle)*(pointY-originY)
    
    return rotatedX, rotatedY

        
def isInside(x, y, poly):
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

brojOsoba=input('Nad koliko osoba zelite vrsiti test? ')
idOsoba=np.zeros(brojOsoba)
for i in range(0, brojOsoba):
    #idOsoba[i]=input('Unesite id zeljene osobe: ')
    idOsoba[i]=database[random.randint(0, 5550723),1]
print idOsoba


brojZapisa=0
for i in range(0, database.shape[0]):
    if database[i,1] in idOsoba and database[i,5]>400 and database[i,2]>=30000:
        brojZapisa=brojZapisa+1


brojIter=0
lijevo=False
ins=np.zeros((brojZapisa, 2, 50, 50))
outs1s=np.zeros((brojZapisa, 2))
outs2s=np.zeros((brojZapisa, 2))
outs3s=np.zeros((brojZapisa, 2))
outs4s=np.zeros((brojZapisa, 2))
outs5s=np.zeros((brojZapisa, 2))
centarRed, centarStupac=39, 25

for i in range(0, database.shape[0]):
    if database[i,1] in idOsoba and database[i,5]>400 and database[i,2]>=30000:
        trenutnaOsoba=database[i,1]
        pocetnoVrijeme=database[i,0]
        vrijeme=datetime.datetime.utcfromtimestamp(database[i,0]).strftime('%Y-%m-%d %H:%M:%S')
        print "U trenutku ", vrijeme, " pozicija je ", database[i,2], "x, ", database[i,3], "y"
        osobaX, osobaY, osobaKut=database[i,2], database[i,3], database[i,6]
        if osobaKut<0:
            osobaKut=2*np.pi-abs(osobaKut)
            
        if osobaKut>np.pi/2 and osobaKut<=(3*np.pi)/2:
            polygon=getPoints(osobaX, osobaY, np.pi)
            lijevo=True
        else:
            polygon=getPoints(osobaX, osobaY, 0)
        #polygonCentered=getRelativePoints(np.pi/2)
        
        
        if i+5000>database.shape[0]:
            for j in range(i-5000, database.shape[0]):
                if isInside(database[j,2], database[j,3], polygon) and database[i,0]==database[j,0] and database[i,1]!=database[j,1]:
                    gostX=database[j,2]-osobaX
                    gostY=database[j,3]-osobaY
                    if lijevo:
                        gostX=gostX*-1
                        gostY=gostY*-1
                    print "U blizini je id ", database[j,1], " rel. polozaj ", gostX, "x, ", gostY*-1, "y, brzine ", database [j,5], "mm/s, smjer kretanja ", database[j,6], " rad"
                    try:
                        ins[brojIter,0,int(centarRed-round(gostX/100)),int(centarStupac-round(gostY/100))]=database[j,5]/1000
                        ins[brojIter,1,int(centarRed-round(gostX/100)),int(centarStupac-round(gostY/100))]=database[j,6]
                    except:
                        print "Index ne moze biti 50!"
        else:
            for j in range(i-5000, i+5000):
                if isInside(database[j,2], database[j,3], polygon) and database[i,0]==database[j,0] and database[i,1]!=database[j,1]:
                    gostX=database[j,2]-osobaX
                    gostY=database[j,3]-osobaY
                    if lijevo:
                        gostX=gostX*-1
                        gostY=gostY*-1
                    print "U blizini je id ", database[j,1], " rel. polozaj ", gostX, "x, ", gostY, "y, brzine ", database [j,5], "mm/s, smjer kretanja ", database[j,6], " rad"
                    try:
                        ins[brojIter,0,int(centarRed-round(gostX/100)),int(centarStupac-round(gostY/100))]=database[j,5]/1000
                        ins[brojIter,1,int(centarRed-round(gostX/100)),int(centarStupac-round(gostY/100))]=database[j,6]
                    except:
                        print "Index ne moze biti 50!"
                
        ins[brojIter,0,centarRed,centarStupac]=database[i,5]/1000
        ins[brojIter,1,centarRed,centarStupac]=database[i,6]
        
        zbrojBrzina, brojIterj=0, 0
        if i+10000>database.shape[0]:
            for j in range(i, database.shape[0]):
                if database[j,1]==trenutnaOsoba:
                    zbrojBrzina=zbrojBrzina+database[j,5]
                    brojIterj=brojIterj+1
                    if pocetnoVrijeme+1>=database[j,0]:
                        if lijevo:
                            outs1s[brojIter,0]=((database[j,2]-osobaX)*-1)/1000
                            outs1s[brojIter,1]=((database[j,3]-osobaY)*-1)/1000
                        else:
                            outs1s[brojIter,0]=(database[j,2]-osobaX)/1000
                            outs1s[brojIter,1]=(database[j,3]-osobaY)/1000
                    elif pocetnoVrijeme+2>=database[j,0]:
                        if lijevo:
                            outs2s[brojIter,0]=((database[j,2]-osobaX)*-1)/1000
                            outs2s[brojIter,1]=((database[j,3]-osobaY)*-1)/1000
                        else:
                            outs2s[brojIter,0]=(database[j,2]-osobaX)/1000
                            outs2s[brojIter,1]=(database[j,3]-osobaY)/1000
                        #print "Srednja brzina nakon 2 sekunde je: ", zbrojBrzina/brojIterj, " mm/s"
                    elif pocetnoVrijeme+3>=database[j,0]:
                        if lijevo:
                            outs3s[brojIter,0]=((database[j,2]-osobaX)*-1)/1000
                            outs3s[brojIter,1]=((database[j,3]-osobaY)*-1)/1000
                        else:
                            outs3s[brojIter,0]=(database[j,2]-osobaX)/1000
                            outs3s[brojIter,1]=(database[j,3]-osobaY)/1000
                    elif pocetnoVrijeme+4>=database[j,0]:
                        if lijevo:
                            outs4s[brojIter,0]=((database[j,2]-osobaX)*-1)/1000
                            outs4s[brojIter,1]=((database[j,3]-osobaY)*-1)/1000
                        else:
                            outs4s[brojIter,0]=(database[j,2]-osobaX)/1000
                            outs4s[brojIter,1]=(database[j,3]-osobaY)/1000
                    elif pocetnoVrijeme+5>=database[j,0]:
                        if lijevo:
                            outs5s[brojIter,0]=((database[j,2]-osobaX)*-1)/1000
                            outs5s[brojIter,1]=((database[j,3]-osobaY)*-1)/1000
                        else:
                            outs5s[brojIter,0]=(database[j,2]-osobaX)/1000
                            outs5s[brojIter,1]=(database[j,3]-osobaY)/1000
                        #print "Srednja brzina nakon 5 sekundi je: ", zbrojBrzina/brojIterj, " mm/s"
        else:
            for j in range(i, i+10000):
                if database[j,1]==trenutnaOsoba:
                    zbrojBrzina=zbrojBrzina+database[j,5]
                    brojIterj=brojIterj+1
                    if pocetnoVrijeme+1>=database[j,0]:
                        if lijevo:
                            outs1s[brojIter,0]=((database[j,2]-osobaX)*-1)/1000
                            outs1s[brojIter,1]=((database[j,3]-osobaY)*-1)/1000
                        else:
                            outs1s[brojIter,0]=(database[j,2]-osobaX)/1000
                            outs1s[brojIter,1]=(database[j,3]-osobaY)/1000
                    elif pocetnoVrijeme+2>=database[j,0]:
                        if lijevo:
                            outs2s[brojIter,0]=((database[j,2]-osobaX)*-1)/1000
                            outs2s[brojIter,1]=((database[j,3]-osobaY)*-1)/1000
                        else:
                            outs2s[brojIter,0]=(database[j,2]-osobaX)/1000
                            outs2s[brojIter,1]=(database[j,3]-osobaY)/1000
                        #print "Srednja brzina nakon 2 sekunde je: ", zbrojBrzina/brojIterj, " mm/s"
                    elif pocetnoVrijeme+3>=database[j,0]:
                        if lijevo:
                            outs3s[brojIter,0]=((database[j,2]-osobaX)*-1)/1000
                            outs3s[brojIter,1]=((database[j,3]-osobaY)*-1)/1000
                        else:
                            outs3s[brojIter,0]=(database[j,2]-osobaX)/1000
                            outs3s[brojIter,1]=(database[j,3]-osobaY)/1000
                    elif pocetnoVrijeme+4>=database[j,0]:
                        if lijevo:
                            outs4s[brojIter,0]=((database[j,2]-osobaX)*-1)/1000
                            outs4s[brojIter,1]=((database[j,3]-osobaY)*-1)/1000
                        else:
                            outs4s[brojIter,0]=(database[j,2]-osobaX)/1000
                            outs4s[brojIter,1]=(database[j,3]-osobaY)/1000
                    elif pocetnoVrijeme+5>=database[j,0]:
                        if lijevo:
                            outs5s[brojIter,0]=((database[j,2]-osobaX)*-1)/1000
                            outs5s[brojIter,1]=((database[j,3]-osobaY)*-1)/1000
                        else:
                            outs5s[brojIter,0]=(database[j,2]-osobaX)/1000
                            outs5s[brojIter,1]=(database[j,3]-osobaY)/1000
                        #print "Srednja brzina nakon 5 sekundi je: ", zbrojBrzina/brojIterj, " mm/s"
        
        outs1s[brojIter,0], outs1s[brojIter,1]=rotateAroundOrigin(0, 0, outs1s[brojIter,0], outs1s[brojIter,1], np.pi/2)
        outs2s[brojIter,0], outs2s[brojIter,1]=rotateAroundOrigin(0, 0, outs2s[brojIter,0], outs2s[brojIter,1], np.pi/2)
        outs3s[brojIter,0], outs3s[brojIter,1]=rotateAroundOrigin(0, 0, outs3s[brojIter,0], outs3s[brojIter,1], np.pi/2)
        outs4s[brojIter,0], outs4s[brojIter,1]=rotateAroundOrigin(0, 0, outs4s[brojIter,0], outs4s[brojIter,1], np.pi/2)
        outs5s[brojIter,0], outs5s[brojIter,1]=rotateAroundOrigin(0, 0, outs5s[brojIter,0], outs5s[brojIter,1], np.pi/2)
        #print "Nakon 1 s rel polozaj: ", outs1s[brojIter,0],"x, ", outs1s[brojIter,1], "y"
        #print "Nakon 2 s rel polozaj: ", outs2s[brojIter,0],"x, ", outs2s[brojIter,1], "y"
        #print "Nakon 3 s rel polozaj: ", outs3s[brojIter,0],"x, ", outs3s[brojIter,1], "y"
        #print "Nakon 4 s rel polozaj: ", outs4s[brojIter,0],"x, ", outs4s[brojIter,1], "y"
        #print "Nakon 5 s rel polozaj: ", outs5s[brojIter,0],"x, ", outs5s[brojIter,1], "y"
        
        brojIter=brojIter+1
        lijevo=False



zaBrisati=np.argwhere(np.sqrt(np.square(outs5s[:,0])+np.square(outs5s[:,1]))<1)
outs5s=np.delete(outs5s, zaBrisati, 0)
ins=np.delete(ins, zaBrisati, 0)

zaBrisati=np.argwhere(outs5s[:,1]<0)
outs5s=np.delete(outs5s, zaBrisati, 0)
ins=np.delete(ins, zaBrisati, 0)

index=np.argwhere(np.abs(np.arctan2(outs5s[:,0], outs5s[:,1]))<0.1)
index2=np.argwhere(np.abs(np.arctan2(outs5s[:,0], outs5s[:,1]))>0.1)
zaBrisati=index[0:int(index.shape[0]-round(index2.shape[0]/0.7-index2.shape[0])),:]
outs5s=np.delete(outs5s, zaBrisati, 0)
ins=np.delete(ins, zaBrisati, 0)

h5fw=h5py.File('insouts.h5', 'w')
h5fw.create_dataset("ins", data=ins, compression='lzf')
h5fw.create_dataset("outs", data=outs5s, compression='lzf')
h5fw.close()