# -*- coding: utf-8 -*-
"""
Created on Tue May  9 17:28:46 2017

@author: luka
"""

import h5py
import numpy as np
from keras.models import Sequential
from keras.layers import Dense, Conv2D, Activation, MaxPooling2D, Flatten

insouts=h5py.File("data/neural_network_insouts.h5", 'r')
ins=insouts['ins']
outs=insouts['outs']
outs1=outs[:,0]/outs[:,1]
outs2=np.arctan2(outs[:,0], outs[:,1])

testX=ins[0:10]
testY=outs[0:10]
#testY=outs1[0:10]
#testY=outs2[0:10]


model=Sequential()

model.add(Conv2D(32, (3, 3), padding='valid', input_shape=(2, 20, 20)))
model.add(Activation('relu'))

model.add(Conv2D(32, (3, 3)))
model.add(Activation('relu'))

model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Flatten())

model.add(Dense(128))
model.add(Activation('relu'))

model.add(Dense(2))
#model.add(Dense(1))
model.add(Activation('linear'))

model.compile(loss='mean_squared_error', optimizer='adadelta')

model.fit(ins, outs, epochs=10, batch_size=32, shuffle='batch')
#model.fit(ins, outs1, epochs=10, batch_size=32, shuffle='batch')
#model.fit(ins, outs2, epochs=10, batch_size=32, shuffle='batch')

model.save_weights('model/pedestrian_model_weights.h5')
model_json = model.to_json()
with open('model/pedestrian_model.json', "w") as json_file:
    json_file.write(model_json)
json_file.close()

result=model.predict(testX)
print result
score=model.evaluate(testX, testY)
print score

insouts.close()
