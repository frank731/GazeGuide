''' Demonstrates how to subscribe to and handle data from gaze and event streams '''
import asyncio
import time
import socket 

import adhawkapi
import adhawkapi.frontend

from scipy.spatial.transform import Rotation as R
import numpy as np
import enum 

from math import isnan

cur_gaze = []
set_gaze = []
cur_rot = []
set_rot = []
last_good_gaze = [0, 0]
last_good_rot = []
eye_gaze_factor = 30
x_angle_thresh = 25
y_angle_thresh = 20
PORT = 1000
IP = "127.0.0.1"
DATA_RECEIVED = False

class UDPProtocol:
    def __init__(self):
        pass

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        global DATA_RECEIVED
        DATA_RECEIVED = True
        print("hellooojijoijoij")

class EulerRotationOrder(enum.IntEnum):
    '''Various Euler rotation orders. lowercase x,y, z stand for the axes of the world coordinate system, and
    uppercase X, Y, and Z stands for the local moving axes'''
    # pylint: disable=invalid-name
    XY = 0  # first rotate around local X, then rotate around local Y axis (this is also known as yx')
    YX = 1  # first rotate around local Y, then rotate around local X axis (this is also known as xy')


def vector_to_angles(xpos, ypos, zpos, rotation_order: EulerRotationOrder = EulerRotationOrder.XY):
    '''
    Converts a gaze vector to [azimuth (yaw), elevation (pitch)] angles based on a specific rotation order and
    a vector defined in our usual backend coordinate system (with X oriented in the positive direction to the right,
    Y oriented in the positive direction going up and Z oriented in the positive direction behind the user). Also note
    that we want the positive yaw to be rotation to the right.
    '''
    azimuth = elevation = np.nan
    if rotation_order == EulerRotationOrder.YX:
        azimuth = np.arctan2(xpos, -zpos)
        elevation = np.arctan2(ypos, np.sqrt(xpos ** 2 + zpos ** 2))
    elif rotation_order == EulerRotationOrder.XY:
        azimuth = np.arctan2(xpos, np.sqrt(ypos ** 2 + zpos ** 2))
        elevation = np.arctan2(ypos, -zpos)
    return [azimuth, elevation]

def check_look_away():
    eye_az_diff = cur_gaze[0] - set_gaze[0]
    eye_el_diff = cur_gaze[1] - set_gaze[1]
    head_roll_diff = cur_rot[0] - set_rot[0] # Tilting head kind of affects position so eyes should compensate a little 
    head_az_diff = cur_rot[1] - set_rot[1]
    head_el_diff = cur_rot[2] - set_rot[2]
    az_diff = eye_az_diff + head_az_diff
    el_diff = eye_el_diff + head_el_diff
    #print(cur_gaze, set_gaze, cur_rot, set_rot, az_diff, el_diff)
    if az_diff >= x_angle_thresh:
        print("Too left")
    elif az_diff <= -x_angle_thresh:
        print("Too right")
    if el_diff >= y_angle_thresh:
        print("Too up")
    elif el_diff <= -y_angle_thresh:
        print("Too down")
class FrontendData:
    ''' BLE Frontend '''    
    def __init__(self):
        # Instantiate an API object
        # TODO: Update the device name to match your device
        self._api = adhawkapi.frontend.FrontendApi(ble_device_name='ADHAWK MINDLINK-289')

        # Tell the api that we wish to receive eye tracking data stream
        # with self._handle_et_data as the handler
        self._api.register_stream_handler(adhawkapi.PacketType.EYETRACKING_STREAM, self._handle_et_data)

        # Tell the api that we wish to tap into the EVENTS stream
        # with self._handle_events as the handler
        self._api.register_stream_handler(adhawkapi.PacketType.EVENTS, self._handle_events)

        # Start the api and set its connection callback to self._handle_tracker_connect/disconnect.
        # When the api detects a connection to a MindLink, this function will be run.
        self._api.start(tracker_connect_cb=self._handle_tracker_connect,
                        tracker_disconnect_cb=self._handle_tracker_disconnect)
        
        self.local = ""


    def shutdown(self):
        '''Shutdown the api and terminate the bluetooth connection'''
        self._api.shutdown()

    @staticmethod
    #TODO Test angle directions, see if eyes move a lot or stay off
    def _handle_et_data(et_data: adhawkapi.EyeTrackingStreamData):
        global cur_gaze, cur_rot, set_gaze, set_rot, eye_gaze_factor, last_good_gaze, last_good_rot
        ''' Handles the latest et data '''
        if et_data.gaze is not None:
            cur_gaze = vector_to_angles(et_data.gaze[0], et_data.gaze[1], et_data.gaze[2])
            cur_gaze = [x * eye_gaze_factor for x in cur_gaze]
            if isnan(cur_gaze[0]):
                cur_gaze = last_good_gaze
            else:
                last_good_gaze = cur_gaze
            if len(set_gaze) == 0:
                set_gaze = cur_gaze
            print("Gaze: ")
            print(cur_gaze)
            #xvec, yvec, zvec, vergence = et_data.gaze
            #print(f'Gaze={xvec:.2f},y={yvec:.2f},z={zvec:.2f},vergence={vergence:.2f}')

        if et_data.imu_quaternion is not None:
            if et_data.eye_mask == adhawkapi.EyeMask.BINOCULAR:
                cur_rot = R.from_quat(et_data.imu_quaternion).as_euler('zyx', degrees=True)
                #(cur_rol, cur_az, cur_el) = 
                if len(set_rot) == 0:
                    set_rot = cur_rot
                print("Rotation: ")
                print(cur_rot)
                #x, y, z, w = et_data.imu_quaternion
                #print(f'IMU: roll={cur_rol:.2f},azimuth={cur_az:.2f},elevation={cur_el:.2f}')
        check_look_away()

    @staticmethod
    def _handle_events(event_type, timestamp, *args):
        if event_type == adhawkapi.Events.BLINK:
            duration = args[0]
            #print(f'Got blink: {timestamp} {duration}')
        if event_type == adhawkapi.Events.EYE_CLOSED:
            eye_idx = args[0]
            #print(f'Eye Close: {timestamp} {eye_idx}')
        if event_type == adhawkapi.Events.EYE_OPENED:
            eye_idx = args[0]
            #print(f'Eye Open: {timestamp} {eye_idx}')

    def _handle_tracker_connect(self):
        print("Tracker connected")
        self._api.set_et_stream_rate(2, callback=lambda *args: None)

        self._api.set_et_stream_control([
            adhawkapi.EyeTrackingStreamTypes.GAZE,
            adhawkapi.EyeTrackingStreamTypes.EYE_CENTER,
            adhawkapi.EyeTrackingStreamTypes.PUPIL_DIAMETER,
            adhawkapi.EyeTrackingStreamTypes.IMU_QUATERNION,
        ], True, callback=lambda *args: None)

        #self._api.set_event_control(adhawkapi.EventControlBit.BLINK, 1, callback=lambda *args: None)
        #self._api.set_event_control(adhawkapi.EventControlBit.EYE_CLOSE_OPEN, 1, callback=lambda *args: None)

    def _handle_tracker_disconnect(self):
        print("Tracker disconnected")


async def main():
    ''' App entrypoint '''
    frontend = FrontendData()

    print("Starting UDP server")

    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    udp_endpoint = await asyncio.start_datagram_endpoint(
        lambda: UDPProtocol(),  # Use a simple protocol
        local_addr=(IP, PORT)
    )

    try:
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        frontend.shutdown()

if __name__ == '__main__':
    asyncio.run(main())