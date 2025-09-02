import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

# தரவுகள்: XOR பிரச்சனை
X = [[0,0], [0,1], [1,0], [1,1]]
Y = [0, 1, 1, 0]

# மாடல் உருவாக்கல்
model = Sequential()
model.add(Dense(4, input_dim=2, activation='relu'))
model.add(Dense(1, activation='sigmoid'))

# மாடல் தொகுத்தல்
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

# மாடல் பயிற்சி
model.fit(X, Y, epochs=1000, verbose=0)

# மதிப்பீடு
loss, accuracy = model.evaluate(X, Y)
print("Loss:", loss)
print("Accuracy:", accuracy)

# கணிப்பு
predictions = model.predict(X)
print("Predictions:", predictions)
