"""An intentional regression exercise, not an observed Qiskit defect."""
from qiskit import QuantumCircuit


def prepare_state():
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.cx(0, 1)
    return circuit
