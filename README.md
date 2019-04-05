# conductor
Software package for the selection of targets to observe using SONG

The main module is the conductor.py which is written as a backgroud process. 

There is a potential memory leak in the pyephem package which is causing the conductor to use a lot of memory. 
The code will at each loop check the used memory consumption and if above a specific level it will restart the conductor. 

