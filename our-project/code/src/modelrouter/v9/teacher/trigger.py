"""Low-frequency assessment from completed generations and observed events."""
from __future__ import annotations

from modelrouter.v9.runtime.context import TEST_COMMAND, visible_history


class TeacherTrigger:
    def __init__(self, initial_generations=3):
        self.initial_generations = initial_generations
        self.reset(None)

    def reset(self, episode_id):
        self.episode_id = episode_id
        self.generation_count = 0
        self.last_attempt_generation = None
        self.last_signals = None

    @staticmethod
    def signals(state):
        history = visible_history(state)
        tests = [step for step in history
                 if TEST_COMMAND.search(step.tool_action)]
        verification = None
        if tests:
            step = tests[-1]
            verification = (step.step_index, step.tool_action,
                            step.tool_exit_code, step.tool_observation)
        errors = [step for step in history if step.tool_exit_code != 0]
        repeated = None
        if len(errors) >= 2:
            first, second = errors[-2:]
            first_error = (first.tool_action.strip(), first.tool_exit_code,
                           first.tool_observation.strip())
            second_error = (second.tool_action.strip(), second.tool_exit_code,
                            second.tool_observation.strip())
            if first_error == second_error:
                repeated = (second.step_index, second_error)
        return state.current_phase, verification, repeated

    def reason(self, state):
        if state.episode_id != self.episode_id:
            self.reset(state.episode_id)
        if state.status not in ("INITIALIZED", "RUNNING") or state.steps_remaining <= 1:
            return None
        if self.generation_count < self.initial_generations:
            return None
        if (self.last_attempt_generation is not None
                and self.generation_count - self.last_attempt_generation < self.initial_generations):
            return None
        if self.last_signals is None:
            return "INITIAL_THREE_GENERATIONS"
        phase, verification, repeated = self.signals(state)
        old_phase, old_verification, old_repeated = self.last_signals
        if verification is not None and verification != old_verification:
            return "NEW_VERIFICATION_RESULT"
        if repeated is not None and repeated != old_repeated:
            return "REPEATED_ERROR"
        if phase != old_phase:
            return "PHASE_CHANGED"
        return None

    def record_attempt(self, state):
        self.last_attempt_generation = self.generation_count
        self.last_signals = self.signals(state)

    def after_generation(self):
        self.generation_count += 1
