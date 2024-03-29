# (C) Copyright IBM 2020.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.
#
# Modifications copyright (C) 2023 University of Illinois at Urbana-Champaign
# Author: Andrew Lytle

""" DensePauliExpectation Class """

import logging
from typing import Union

import numpy as np

# from qiskit.opflow.converters.new_abelian_grouper import NewAbelianGrouper
# from qiskit.opflow.converters.abelian_grouper import AbelianGrouper
# from qiskit.opflow.converters.pauli_basis_change import PauliBasisChange
# from qiskit.opflow.converters.new_pauli_basis_change import PauliBasisChange
from qiskit.opflow.expectations.expectation_base import ExpectationBase
from qiskit.opflow.list_ops.composed_op import ComposedOp
from qiskit.opflow.list_ops.list_op import ListOp
from qiskit.opflow.operator_base import OperatorBase
from qiskit.opflow.primitive_ops.pauli_sum_op import PauliSumOp
from qiskit.opflow.primitive_ops.primitive_op import PrimitiveOp
from qiskit.opflow.state_fns.operator_state_fn import OperatorStateFn
from qiskit.opflow.state_fns.state_fn import StateFn

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)
stream_handler = logging.StreamHandler()
log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
formatter = logging.Formatter(log_format)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

import sys, os
from dense_ev.dense_grouper import DenseGrouper
from dense_ev.dense_pauli_basis_change import DensePauliBasisChange


class DensePauliExpectation(ExpectationBase):
    r"""
    An Expectation converter for Pauli-basis observables by changing Pauli measurements to a
    diagonal ({Z, I}^n) basis and appending circuit post-rotations to the measured state function.
    Optionally groups the Paulis with the same post-rotations (those that commute with one
    another, or form Abelian groups) into single measurements to reduce circuit execution
    overhead.

    """

    def __init__(self, group_paulis: bool = True) -> None:
        """
        Args:
            group_paulis: Whether to group the Pauli measurements into commuting sums, which all
                have the same diagonalizing circuit.

        """
        self._grouper = DenseGrouper() if group_paulis else None

    def convert(self, operator: OperatorBase) -> OperatorBase:
        """Accepts an Operator and returns a new Operator with the Pauli measurements replaced by
        diagonal Pauli post-rotation based measurements so they can be evaluated by sampling and
        averaging.

        Args:
            operator: The operator to convert.

        Returns:
            The converted operator.
        """
        if isinstance(operator, ListOp):
            logger.debug(f"isinstance {operator}, ListOp")
            return operator.traverse(self.convert).reduce()

        if isinstance(operator, OperatorStateFn) and operator.is_measurement:
            # Change to Pauli representation if necessary
            if (
                isinstance(operator.primitive, (ListOp, PrimitiveOp))
                and not isinstance(operator.primitive, PauliSumOp)
                and {"Pauli", "SparsePauliOp"} < operator.primitive_strings()
            ):
                logger.debug(f"isinstance {operator.primitive}, (ListOp...)")
                logger.warning(
                    "Measured Observable is not composed of only Paulis, converting to "
                    "Pauli representation, which can be expensive."
                )
                # Setting massive=False because this conversion is implicit. User can perform this
                # action on the Observable with massive=True explicitly if they so choose.
                pauli_obsv = operator.primitive.to_pauli_op(massive=False)
                operator = StateFn(
                    pauli_obsv, is_measurement=True, coeff=operator.coeff
                )

            if self._grouper and isinstance(operator.primitive, (ListOp, PauliSumOp)):
                logger.debug(f"grouper, isinstance {operator.primitive}")
                grouped = self._grouper.convert(operator.primitive)
                logger.debug(f"grouped: {grouped}")
                operator = StateFn(grouped, is_measurement=True, coeff=operator.coeff)

            # Convert the measurement into diagonal basis (PauliBasisChange chooses
            # this basis by default).
            logger.debug("cob")
            logger.debug(operator)
            cob = DensePauliBasisChange(
                replacement_fn=DensePauliBasisChange.measurement_replacement_fn
            )
            logger.info(f"cob._destination: {cob._destination}")
            logger.info(f"cob: {cob}")
            return cob.convert(operator).reduce()

        return operator

    def compute_variance(self, exp_op: OperatorBase) -> Union[list, float, np.ndarray]:
        def sum_variance(operator):
            if isinstance(operator, ComposedOp):
                sfdict = operator.oplist[1]
                measurement = operator.oplist[0]
                average = np.asarray(measurement.eval(sfdict))
                variance = sum(
                    (v * (np.asarray(measurement.eval(b)) - average)) ** 2
                    for (b, v) in sfdict.primitive.items()
                )
                return operator.coeff * variance

            elif isinstance(operator, ListOp):
                return operator.combo_fn([sum_variance(op) for op in operator.oplist])

            return 0.0

        return sum_variance(exp_op)
