# core_basic_window.py
import os, sys
import time
import olympe
os.environ["RAYLIB_BIN_PATH"] = "raylib-2.0.0-Linux-amd64/lib/"
import raylibpy
from olympe.messages.ardrone3.Piloting import *
from olympe.messages.battery import *

window_height = 480      #window width and height for window initalization
window_width = 600
closewindow = False     #if the quit command has been entered
connected = False       #if the drone has been connected
color = raylibpy.Color(0xcf, 0x5e, 0x02, 255)
DRONE_IP = os.environ.get("DRONE_IP", "192.168.42.1")


def main():

    raylibpy.init_window(window_width, window_height, "TERMINATOR - GROUND CONTROL STATION")

    raylibpy.set_target_fps(60)

    #render splash screen
    for x in range(50):
        raylibpy.begin_drawing()
        raylibpy.clear_background(raylibpy.BLACK)
        raylibpy.draw_text("WELCOME TO", 160, 80, 20, color)

        raylibpy.draw_rectangle_lines(138, 108, 315, 32, color)
        raylibpy.draw_text("TERMINATOR - GCS", 140, 110, 30, color)

        raylibpy.end_drawing()

    #render wifi connect prompt
    while not raylibpy.is_key_pressed(raylibpy.KEY_ENTER):
        raylibpy.begin_drawing()
        #raylibpy.clear_background(raylibpy.BLACK)
        raylibpy.draw_text("PLEASE CONNECT TO DRONE WIFI\n         AND PRESS ENTER",120, 200, 20, color)
        raylibpy.end_drawing()

    drone = olympe.Drone(DRONE_IP)
    drone.connect()
    
    flying = False

    x = 0


    #begin flight mode
    while not raylibpy.window_should_close(): #remember to fix this later

        #reset the PCMD parameters (defaults to no movement)
        pitch = 0
        yaw  = 0
        roll = 0
        gaz = 0


        #take keypresses
        if raylibpy.is_key_pressed(raylibpy.KEY_T):      #toggle takeoff land
            if flying == False:
                flying = True
                drone(TakeOff())        #if not flying, takeoff
            else:
                flying = False
                drone(Landing())        #if flying, land

            time.sleep(5)

        #yaw keypress checks
        if raylibpy.is_key_down(raylibpy.KEY_Q):
            yaw = -50
        if raylibpy.is_key_down(raylibpy.KEY_E):
            yaw = 50

        #pitch keypress checks
        if raylibpy.is_key_down(raylibpy.KEY_W):
            pitch = 20
        if raylibpy.is_key_down(raylibpy.KEY_S):
            pitch = -20
        
        #roll keypress checks
        if raylibpy.is_key_down(raylibpy.KEY_A):
            roll = -20
        if raylibpy.is_key_down(raylibpy.KEY_D):
            roll = 20
        
        #throttle keypress checks
        if raylibpy.is_key_down(raylibpy.KEY_LEFT_SHIFT):
            gaz = 20
        if raylibpy.is_key_down(raylibpy.KEY_LEFT_CONTROL):
            gaz = -20

        #initiate ctrl commands
        if flying:
            drone(PCMD(1, roll, pitch, yaw, gaz, 0))


        #initate display commands
        raylibpy.begin_drawing()
        raylibpy.clear_background(raylibpy.BLACK)
        raylibpy.draw_text("Flying - " + str(flying), 10, 10, 20, color)

        #battery status indicator
        raylibpy.draw_text(str(drone(voltage().voltage)) + " Volts", 10, 40, 20, color)

        raylibpy.end_drawing()

    
    #on termination, land if not landed and disconnect
    drone(Landing)
    drone(disconnect())
    #close window
    raylibpy.close_window()


if __name__ == "__main__":
    main()

