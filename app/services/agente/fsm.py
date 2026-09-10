"""Máquina de Estados Finitos (FSM) formal para el Agente.

Define los estados válidos y la matriz estricta de transiciones permitidas,
eliminando comportamientos impredecibles y transiciones inválidas.
"""

from enum import Enum


class AgentState(str, Enum):
    IDLE = "IDLE"
    UNDERSTANDING = "UNDERSTANDING"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    READY_TO_CONFIRM = "READY_TO_CONFIRM"
    EXECUTING = "EXECUTING"
    EXECUTED = "EXECUTED"

    # Estados terminales / de error
    OUT_OF_SCOPE = "OUT_OF_SCOPE"
    INVALIDATED = "INVALIDATED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


# Matriz de transiciones permitidas
VALID_TRANSITIONS: dict[AgentState, set[AgentState]] = {
    AgentState.IDLE: {
        AgentState.UNDERSTANDING,
        AgentState.NEEDS_CLARIFICATION,
        AgentState.READY_TO_CONFIRM,
        AgentState.OUT_OF_SCOPE,
        AgentState.FAILED,
        AgentState.IDLE,
    },
    AgentState.UNDERSTANDING: {
        AgentState.NEEDS_CLARIFICATION,
        AgentState.READY_TO_CONFIRM,
        AgentState.OUT_OF_SCOPE,
        AgentState.FAILED,
        AgentState.IDLE,
    },
    AgentState.NEEDS_CLARIFICATION: {
        AgentState.UNDERSTANDING,
        AgentState.NEEDS_CLARIFICATION,
        AgentState.READY_TO_CONFIRM,
        AgentState.REJECTED,
        AgentState.INVALIDATED,
        AgentState.FAILED,
        AgentState.IDLE,
    },
    AgentState.READY_TO_CONFIRM: {
        AgentState.EXECUTING,
        AgentState.REJECTED,
        AgentState.INVALIDATED,
        AgentState.FAILED,
        AgentState.IDLE,
    },
    AgentState.EXECUTING: {
        AgentState.EXECUTED,
        AgentState.INVALIDATED,
        AgentState.FAILED,
    },
    # Estados finales: pueden reiniciar a cualquier estado en un nuevo comando
    AgentState.EXECUTED: {AgentState.IDLE, AgentState.UNDERSTANDING, AgentState.READY_TO_CONFIRM, AgentState.NEEDS_CLARIFICATION},
    AgentState.OUT_OF_SCOPE: {AgentState.IDLE, AgentState.UNDERSTANDING, AgentState.READY_TO_CONFIRM},
    AgentState.INVALIDATED: {AgentState.IDLE, AgentState.UNDERSTANDING, AgentState.READY_TO_CONFIRM},
    AgentState.REJECTED: {AgentState.IDLE, AgentState.UNDERSTANDING, AgentState.READY_TO_CONFIRM},
    AgentState.FAILED: {AgentState.IDLE, AgentState.UNDERSTANDING, AgentState.READY_TO_CONFIRM},
}


class InvalidStateTransitionError(Exception):
    def __init__(self, from_state: AgentState, to_state: AgentState):
        super().__init__(f"Transición no permitida en la FSM: de '{from_state}' hacia '{to_state}'")
        self.from_state = from_state
        self.to_state = to_state


def validate_transition(from_state: AgentState | str, to_state: AgentState | str) -> bool:
    f_state = AgentState(from_state) if isinstance(from_state, str) else from_state
    t_state = AgentState(to_state) if isinstance(to_state, str) else to_state

    allowed = VALID_TRANSITIONS.get(f_state, set())
    if t_state not in allowed:
        raise InvalidStateTransitionError(f_state, t_state)
    return True
