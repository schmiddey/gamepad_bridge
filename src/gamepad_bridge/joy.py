import numpy as np #for signum


class Joy:
  #axis
  stick_l_x: float = 0.0
  stick_l_y: float = 0.0
  stick_r_x: float = 0.0
  stick_r_y: float = 0.0
  trigger_l: float = 0.0
  trigger_r: float = 0.0
  #buttons
  btn_a: bool = False
  btn_b: bool = False
  btn_x: bool = False
  btn_y: bool = False
  btn_l1: bool = False
  btn_r1: bool = False
  btn_l2: bool = False
  btn_r2: bool = False
  btn_stick_l: bool = False
  btn_stick_r: bool = False
  btn_share: bool = False
  btn_options: bool = False
  btn_up: bool = False
  btn_down: bool = False
  btn_left: bool = False
  btn_right: bool = False


  def print_data(self):
    print("###################################")
    print(f"stick_l_x: {self.stick_l_x}")
    print(f"stick_l_y: {self.stick_l_y}")
    print(f"stick_r_x: {self.stick_r_x}")
    print(f"stick_r_y: {self.stick_r_y}")
    print(f"trigger_l: {self.trigger_l}")
    print(f"trigger_r: {self.trigger_r}")
    print(f"btn_a: {self.btn_a}")
    print(f"btn_b: {self.btn_b}")
    print(f"btn_x: {self.btn_x}")
    print(f"btn_y: {self.btn_y}")
    print(f"btn_l1: {self.btn_l1}")
    print(f"btn_r1: {self.btn_r1}")
    print(f"btn_l2: {self.btn_l2}")
    print(f"btn_r2: {self.btn_r2}")
    print(f"btn_stick_l: {self.btn_stick_l}")
    print(f"btn_stick_r: {self.btn_stick_r}")
    print(f"btn_share: {self.btn_share}")
    print(f"btn_options: {self.btn_options}")
    print(f"btn_up: {self.btn_up}")
    print(f"btn_down: {self.btn_down}")
    print(f"btn_left: {self.btn_left}")
    print(f"btn_right: {self.btn_right}")




  def from_list(self, data, deadzone=30):
    raise NotImplementedError("from_list not implemented")

