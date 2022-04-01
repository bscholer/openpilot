#!/usr/bin/env python3
import unittest

from cereal import car, log
from selfdrive.controls.lib.events import Events
from selfdrive.controls.controlsd import Controls

ButtonEvent = car.CarState.ButtonEvent
ButtonType = car.CarState.ButtonEvent.Type
State = log.ControlsState.OpenpilotState
EventName = car.CarEvent.EventName

ALL_STATES = (State.disabled, State.preEnabled, State.enabled, State.softDisabling, State.overriding)
ACTIVE_STATES = (State.enabled, State.overriding, State.softDisabling)
ENABLED_STATES = (State.preEnabled, *ACTIVE_STATES)


class WrappedControls(Controls):
  def __init__(self):
    self.state = State.disabled
    self.enabled = False
    self.active = False
    self.soft_disable_timer = 0
    self.events = Events()

    self.CP = car.CarParams()
    self.is_metric = False
    self.button_timers = {}
    self.v_cruise_kph = 0


class TestCruiseButtons(unittest.TestCase):
  CS = car.CarState()

  def setUp(self):
    self.controlsd = WrappedControls()

  def test_disable_immediately(self):
    for state in ALL_STATES:
      # IMMEDIATE_DISABLE
      self.controlsd.state = state
      self.controlsd.events.add(EventName.controlsMismatch)
      self.controlsd.state_transition(self.CS)
      self.assertEqual(State.disabled, self.controlsd.state)

      self.controlsd.events.clear()

      # USER_DISABLE
      self.controlsd.state = state
      self.controlsd.events.add(EventName.buttonCancel)
      self.controlsd.state_transition(self.CS)
      self.assertEqual(State.disabled, self.controlsd.state)


if __name__ == "__main__":
  unittest.main()
