#!/usr/bin/env python3
import unittest

from cereal import car, log
from selfdrive.controls.lib.events import ET
from selfdrive.controls.controlsd import Controls, ENABLED_STATES

State = log.ControlsState.OpenpilotState

# The event types that maintain the current state
MAINTAIN_STATES = {State.enabled: None, State.disabled: None, State.overriding: ET.OVERRIDE,
                   State.softDisabling: ET.SOFT_DISABLE, State.preEnabled: ET.PRE_ENABLE}
ALL_STATES = (State.disabled, *ENABLED_STATES)


class Events:
  # Provides identical API for state_transition
  def __init__(self):
    self.et = []

  def any(self, event_type):
    return event_type in self.et


class TestControls(Controls):
  def __init__(self):  # pylint: disable=super-init-not-called
    self.state = State.disabled
    self.enabled = False
    self.active = False
    self.events = Events()

    self.CP = car.CarParams()
    self.is_metric = False
    self.button_timers = {}
    self.v_cruise_kph = 0


class TestStateMachine(unittest.TestCase):
  CS = car.CarState()

  def setUp(self):
    self.controlsd = TestControls()
    self.controlsd.soft_disable_timer = 200  # make sure timer never causes state to change

  def test_immediate_disable(self):
    for state in ALL_STATES:
      self.controlsd.events.et = [MAINTAIN_STATES[state], ET.IMMEDIATE_DISABLE]
      self.controlsd.state = state
      self.controlsd.state_transition(self.CS)
      self.assertEqual(State.disabled, self.controlsd.state)

  def test_user_disable(self):
    for state in ALL_STATES:
      self.controlsd.events.et = [MAINTAIN_STATES[state], ET.USER_DISABLE]
      self.controlsd.state = state
      self.controlsd.state_transition(self.CS)
      self.assertEqual(State.disabled, self.controlsd.state)

  def test_no_entry(self):
    for et in [ET.ENABLE, ET.PRE_ENABLE, ET.OVERRIDE]:
      self.controlsd.events.et = [ET.NO_ENTRY, et]
      self.controlsd.state_transition(self.CS)
      self.assertEqual(self.controlsd.state, State.disabled)

  def test_maintain_states(self):
    for state in ALL_STATES:
      self.controlsd.state = state
      self.controlsd.events.et = [MAINTAIN_STATES[state]]
      self.controlsd.state_transition(self.CS)
      self.assertEqual(self.controlsd.state, state)


if __name__ == "__main__":
  unittest.main()
