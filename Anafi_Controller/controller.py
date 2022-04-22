# core_basic_window.py
import os, sys
import time
import math
import olympe
os.environ["RAYLIB_BIN_PATH"] = "raylib-2.0.0-Linux-amd64/lib/"
import raylibpy
from olympe.messages.ardrone3.Piloting import *
from olympe.messages.battery import *
from olympe.messages.common.CommonState import *
from olympe.messages.ardrone3.PilotingState import *

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
    
    corrective = False #take corrective action

    x = 0

    #olympe.Drone.streaming.start()

    #begin flight mode
    while not raylibpy.window_should_close(): #remember to fix this later

        #reset the PCMD parameters (defaults to no movement)
        pitch = 0
        yaw  = 0
        roll = 0
        gaz = 0

        inX = False #is keypress taken for each axis
        inY = False
        inZ = False

        drone_speed = drone.get_state(SpeedChanged) #take speed for drift compensation
        #change speed relative to drone instead of relative to fixed space
        rotation = drone.get_state(AttitudeChanged)
        theta = rotation.get('yaw')
        drone_speed['speedX'] = math.sin(theta) * drone_speed.get('speedY') + math.cos(theta) * drone_speed.get('speedX')
        drone_speed['speedY'] = math.sin(theta) * drone_speed.get('speedX') + math.cos(theta) * drone_speed.get('speedY')

        #take keypresses
        if raylibpy.is_key_pressed(raylibpy.KEY_T):      #toggle takeoff land
            if flying == False:
                flying = True
                drone(TakeOff())        #if not flying, takeoff
            else:
                flying = False
                drone(Landing())        #if flying, land

            time.sleep(3)

        if raylibpy.is_gamepad_button_pressed(0,5):      #toggle takeoff land
            if flying == False:
                flying = True
                drone(TakeOff())        #if not flying, takeoff
            else:
                flying = False
                drone(Landing())        #if flying, land

            time.sleep(3)

        if raylibpy.is_key_pressed(raylibpy.KEY_TAB):       #toggle flight assist
            corrective = not corrective

        #if gamepad is not availible do this
        if not raylibpy.is_gamepad_available(0):
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
        else:
            #if a gamepad is attached
            gaz = -1 * int(raylibpy.get_gamepad_axis_movement(0,1) * 50) #by default input is inverted for some reason
            yaw = int(raylibpy.get_gamepad_axis_movement(0,0) * 50)
            pitch = -1 * int(raylibpy.get_gamepad_axis_movement(0,4) * 50)
            roll = int(raylibpy.get_gamepad_axis_movement(0,3) * 50)


        if corrective:
            if not (raylibpy.get_gamepad_axis_movement(0, 4) > 0.01 or raylibpy.get_gamepad_axis_movement(0, 4) < -0.01):
                pitch = int(-1 * drone_speed.get('speedX') * 50)
            
            if not (raylibpy.get_gamepad_axis_movement(0, 3) > 0.01 or raylibpy.get_gamepad_axis_movement(0, 3) < -0.01):
                roll = int(1 * drone_speed.get('speedY') * 50)

        #initiate ctrl commands
        if flying:
            drone(PCMD(1, roll, pitch, yaw, gaz, 0))


        #initate display commands
        raylibpy.begin_drawing()
        raylibpy.clear_background(raylibpy.BLACK)
        #raylibpy.draw_text("Flying - " + str(flying), 10, 10, 20, color)

        #if not flying
        if not flying:
            raylibpy.draw_rectangle_lines(8,8, 90, 24, color)
            raylibpy.draw_text("Idle", 10, 10, 20, color)
        else:
            raylibpy.draw_rectangle(8, 8, 90, 24, color)
            raylibpy.draw_text("Flying", 10, 10, 20, raylibpy.BLACK)

        #else display idle

        #battery status indicator
        #vt = drone(voltage())
        raylibpy.draw_text(str(drone.get_state(BatteryStateChanged)), -150, 450, 20, color)
        raylibpy.draw_rectangle(0, 450, 100, 20, raylibpy.BLACK)
        raylibpy.draw_text("Battery", 10, 450, 20, color)
        raylibpy.draw_rectangle(130, 450, 60, 40, raylibpy.BLACK)
        raylibpy.draw_text("%", 130, 450, 20, color)

        #xyz velocity
        drone_speed = drone.get_state(SpeedChanged)
        raylibpy.draw_text("X vel. " + str(drone_speed.get('speedX')), 300, 10, 20, color)
        raylibpy.draw_text("Y vel. " + str(drone_speed.get('speedY')), 300, 40, 20, color)
        raylibpy.draw_text("Z vel. " + str(drone_speed.get('speedZ')), 300, 70, 20, color)
        
        #draw if flight assist (corrective) is on
        if corrective:
            raylibpy.draw_text("Flight Assist ON", 10, 40, 20, color)
        else:
            raylibpy.draw_text("Flight Assist OFF", 10, 40, 20, color)

        raylibpy.end_drawing()

    
    #on termination, land if not landed and disconnect
    drone(Landing())
    drone(disconnect())
    #close window
    raylibpy.close_window()


if __name__ == "__main__":
    main()

