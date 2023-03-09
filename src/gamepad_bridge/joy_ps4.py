
import gamepad_bridge.joy as joy
import numpy as np #for signum



class JoyPS4(joy.Joy):

  def from_list(self, data, deadzone=30):
    # print("###################################")
    # print(data)
    # btn_1 = data[5]
    # btn_2 = data[6]
    # print(bin(btn_1).zfill(8))
    # print(bin(btn_2).zfill(8))
    def convert_to_float(x):
      tmp_val = x - 128
      if abs(tmp_val) < deadzone:
        return 0.0
      
      tmp_val = tmp_val - np.sign(tmp_val) * deadzone
      
      return tmp_val / (127 - deadzone)
    #lamda for constrain
    constrain = lambda x: min(1.0 , max(-1.0, x))

    self.stick_l_x = constrain(convert_to_float(data[1]))
    self.stick_l_y = -1 * constrain(convert_to_float(data[2]))
    self.stick_r_x = constrain(convert_to_float(data[3]))
    self.stick_r_y = -1 * constrain(convert_to_float(data[4]))
    self.trigger_r = data[9] / 255
    self.trigger_l = data[8] / 255

    #buttons
    self.btn_a     = bool(data[5] & 0b00100000)
    self.btn_b     = bool(data[5] & 0b01000000)
    self.btn_x     = bool(data[5] & 0b10000000)
    self.btn_y     = bool(data[5] & 0b00010000)
    tmp_cross = data[5] & 0b00001111
    self.btn_up    = not bool(tmp_cross)
    self.btn_right = tmp_cross == 0b0010#bool(data[5] & 0b00000010)
    self.btn_left  = tmp_cross == 0b0110#bool(data[5] & 0b00000100)
    self.btn_down  = tmp_cross == 0b0100#bool(data[5] & 0b00000110)

    self.btn_l1    = bool(data[6] & 0b00000001)
    self.btn_r1    = bool(data[6] & 0b00000010)
    self.btn_l2    = bool(data[6] & 0b00000100)
    self.btn_r2    = bool(data[6] & 0b00001000)
    self.btn_share = bool(data[6] & 0b00010000)
    self.btn_options = bool(data[6] & 0b00100000)
    self.btn_stick_l = bool(data[6] & 0b01000000)
    self.btn_stick_r = bool(data[6] & 0b10000000)