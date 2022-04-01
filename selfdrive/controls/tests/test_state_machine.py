#!/usr/bin/env python3
from typing import Set, Optional
import unittest

from cereal import car, log
from selfdrive.controls.lib.events import ET
from selfdrive.controls.controlsd import Controls

State = log.ControlsState.OpenpilotState
EventName = car.CarEvent.EventName

ALL_STATES = (State.disabled, State.preEnabled, State.enabled, State.softDisabling, State.overriding)
ACTIVE_STATES = (State.enabled, State.overriding, State.softDisabling)
ENABLED_STATES = (State.preEnabled, *ACTIVE_STATES)


# def get_event_with_event_types(event_types: Set[str]):
#   for ev in EVENTS:
#     if event_types == set(EVENTS[ev].keys()):
#       return ev

class Events:
  # Provides identical API for state_transition
  def __init__(self):
    self.et = []

  def any(self, event_type):
    return event_type in self.et


class WrappedControls(Controls):
  def __init__(self):  # pylint: disable=super-init-not-called
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

  def test_disable_any_state(self):
    self.controlsd.events.et = ET.IMMEDIATE_DISABLE
    for state in ALL_STATES:
      self.controlsd.state = state
      self.controlsd.state_transition(self.CS)
      self.assertEqual(State.disabled, self.controlsd.state)

    self.controlsd.events.et = [ET.USER_DISABLE]
    for state in ALL_STATES:
      self.controlsd.state = state
      self.controlsd.state_transition(self.CS)
      self.assertEqual(State.disabled, self.controlsd.state)

  def test_no_entry(self):
    self.controlsd.events.et = [ET.NO_ENTRY, ET.ENABLE, ET.PRE_ENABLE, ET.OVERRIDE]
    self.controlsd.state_transition(self.CS)
    self.assertEqual(self.controlsd.state, State.disabled)


if __name__ == "__main__":
  unittest.main()
