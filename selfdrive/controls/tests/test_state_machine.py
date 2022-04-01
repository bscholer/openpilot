#!/usr/bin/env python3
import unittest

from cereal import car, log
from selfdrive.controls.lib.events import ET
from selfdrive.controls.controlsd import Controls

State = log.ControlsState.OpenpilotState

# The event types that maintain the current state
MAINTAIN_STATES = {State.enabled: None, State.disabled: None, State.overriding: ET.OVERRIDE,
                   State.softDisabling: ET.SOFT_DISABLE, State.preEnabled: ET.PRE_ENABLE}
ALL_STATES = (State.disabled, State.preEnabled, State.enabled, State.softDisabling, State.overriding)


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

  # TODO: this does not pass for preEnabled and overriding
  # def test_soft_disable(self):
  #   # Make sure we can soft disable from each enabled state
  #   for state in ENABLED_STATES:
  #     self.controlsd.state = state
  #     self.controlsd.events.et = [MAINTAIN_STATES[state], ET.SOFT_DISABLE]
  #     self.controlsd.state_transition(self.CS)
  #     self.assertEqual(self.controlsd.state, State.softDisabling)

  def test_no_entry(self):
    self.controlsd.events.et = [ET.NO_ENTRY, ET.ENABLE, ET.PRE_ENABLE, ET.OVERRIDE]
    self.controlsd.state_transition(self.CS)
    self.assertEqual(self.controlsd.state, State.disabled)

  def test_maintain_states(self):
    for state in ALL_STATES:
      self.controlsd.state = state
      self.controlsd.events.et = [MAINTAIN_STATES[state]]
      self.controlsd.state_transition(self.CS)
      self.assertEqual(self.controlsd.state, state)

  def test_default_transitions(self):
    for state in ALL_STATES:
      self.controlsd.state = state
      self.controlsd.state_transition(self.CS)
      self.assertEqual(self.controlsd.state, State.enabled if state != State.disabled else State.disabled)


if __name__ == "__main__":
  unittest.main()
