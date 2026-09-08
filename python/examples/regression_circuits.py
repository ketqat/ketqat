"""A deliberate mutation, not an observed SDK defect or customer incident."""
from qiskit import QuantumCircuit


def baseline():
    circuit = QuantumCircuit(2)
    circuit.h(0)
    circuit.cx(0, 1)
    return circuit


def candidate():
    circuit = QuantumCircuit(2)
    circuit.h(0)  # Deliberately omit the CX to change the output distribution.
    return circuit
