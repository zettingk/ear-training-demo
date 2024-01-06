# Ear Training Demo

This is a demo app created using Python and pygame. It is an app used to train the ears of musicians to be able to be more independent when playing instruments. Currently, it supports two input methods: 1) through a piano emulator drawn by pygame, 2) through a real piano keyboard connected with a midi cable to the device.

Note: there is currently a bug with gaining access to midi output streams and drivers so this project may not currently work on all devices.

# Installation

Download the code and run
```
pip install -r requirements.txt
```
After that, when running the program you must specify it with a *game*. A game is just a file that is stored in the "game" directory to allow the addition of new games in the future. Currently, only two games are supported, *playnotes* which is a game about playing a sequence of notes that you hear (variables such as how many notes to play can all be adjusted inside of the file), while *staffwars* requires you to play the notes that are currently being shown on the staff in order for you to practise your sight-reading skills. You must play the notes in time as they travel left on the staff (there can be multiple notes on the staff at the same time) and if they reach the end you cannot see them any more (in a real application, you would lose lives, points or similar once the note reaches the end of the staff). Other clefs like the bass-clef are not supported. This game is inspired by Staff Wars, a mobile game for practising sight-reading in a similar fashion as described above.
Then, if all goes correctly, the program should be running

Run
```
python3 main.py playnotes
```
Or
```
python3 main.py staffwars
```
To choose your game.

Then, if all succeeded, the program should be running as intended.

This app may be turned into a real, production-ready version in the future.
