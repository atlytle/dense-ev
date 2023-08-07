"""Docstring."""
from qiskit import QuantumCircuit, execute, QuantumRegister, ClassicalRegister
from qiskit_aer import Aer


class Random:
    """Demo random."""

    def __init__(self):
        """Demo random."""
        self.pow = 2
        self.qasm = Aer.get_backend("aer_simulator")

    def run(self, number: int) -> int:
        """Run method."""
        nb_qubits = number
        print("Generate random number")

        circ = QuantumRegister(nb_qubits, "the number")
        meas = ClassicalRegister(nb_qubits, "measurement")
        quant_circ = QuantumCircuit(circ, meas)

        for i in range(0, nb_qubits):
            quant_circ.x(i)
        quant_circ.measure(circ, meas)

        job = execute(quant_circ, self.qasm, shots=1, memory=True)

        result_sim = job.result()
        memory = result_sim.get_memory()
        result = int(memory[0], 2) + 1

        return result

    def __repr__(self):
        return f"Random(circuit of: {self.pow})"
