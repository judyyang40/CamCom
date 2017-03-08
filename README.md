# CamCom
Message transmitter and receiver using LED lights on Zigduino board

Tx -- Implementation of the transmitter
We've used the FSK method to transmit data, with every frame showing different frequencies. 
Every 1/30 second, the frequency is changed, using CTC mode with interrupt handler.
To deal with having two frequencies in a frame, we put a flash of red light every 1/30 seconds to separate frames.
When the red light shows in a frame, there are two frequencies, and we will get a checksum error. 
Our project still is not able to distinguish different frequencies with the red line, so we do it by hand, changing the webcam's height to avoid the red line.

Input: Code our message into the Arduino code, as char array into tx_word

Rx -- Implementation of the receiver
Take out black parts of the image, and obtain a threshold, to get a black and white result.
From top to bottom, find the middle spot of every black and white strip, and take their median to get our original message.
