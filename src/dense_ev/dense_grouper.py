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


"""DenseGrouper Class"""

from typing import List, Tuple, Union, cast

from qiskit.opflow.converters.converter_base import ConverterBase
from qiskit.opflow.evolutions.evolved_op import EvolvedOp
from qiskit.opflow.exceptions import OpflowError
from qiskit.opflow.list_ops.list_op import ListOp
from qiskit.opflow.list_ops.summed_op import SummedOp
from qiskit.opflow.operator_base import OperatorBase
from qiskit.opflow.primitive_ops.pauli_op import PauliOp
from qiskit.opflow.primitive_ops.pauli_sum_op import PauliSumOp
from qiskit.opflow.state_fns.operator_state_fn import OperatorStateFn

from dense_ev.rmatrix import get_groups, get_groups2
from math import log

class DenseGrouper(ConverterBase):
    """The DenseGrouper converts SummedOps into a sum of sums, 
    organized by optimal dense family groupings.

    Meaning, it will traverse the Operator, and when it finds a SummedOp, it will evaluate which of
    the summed sub-Operators commute with one another. It will then convert each of the groups of
    commuting Operators into their own SummedOps, and return the sum-of-commuting-SummedOps.
    This is particularly useful for cases where mutually commuting groups can be handled
    similarly, as in the case of Pauli Expectations, where commuting Paulis have the same
    diagonalizing circuit rotation, or Pauli Evolutions, where commuting Paulis can be
    diagonalized together.
    """

    def __init__(self, traverse: bool = True) -> None:
        """
        Args:
            traverse: Whether to convert only the Operator passed to ``convert``, or traverse
                down that Operator.
        """
        self._traverse = traverse

    def convert(self, operator: OperatorBase) -> OperatorBase:
        """Check if operator is a SummedOp, in which case covert it into a sum of mutually
        commuting sums, or if the Operator contains sub-Operators and ``traverse`` is True,
        attempt to convert any sub-Operators.

        Args:
            operator: The Operator to attempt to convert.

        Returns:
            The converted Operator.
        """
        if isinstance(operator, PauliSumOp):
            return self.group_subops(operator)

        if isinstance(operator, ListOp):
            if isinstance(operator, SummedOp) and all(
                isinstance(op, PauliOp) for op in operator.oplist
            ):
                return self.group_subops(operator)
            elif self._traverse:
                return operator.traverse(self.convert)
        elif isinstance(operator, OperatorStateFn) and self._traverse:
            return OperatorStateFn(
                self.convert(operator.primitive),
                is_measurement=operator.is_measurement,
                coeff=operator.coeff,
            )
        elif isinstance(operator, EvolvedOp) and self._traverse:
            return EvolvedOp(self.convert(operator.primitive), coeff=operator.coeff)
        return operator

    @classmethod
    def group_subops(cls, list_op: Union[ListOp, PauliSumOp]) -> ListOp:
        """Given a ListOp, attempt to group into ListOps of the same type.

        Args:
            list_op: The Operator to group into dense groups

        Returns:
            The grouped Operator.

        Raises:
            OpflowError: If any of list_op's sub-ops is not ``PauliOp``.
        """
        if isinstance(list_op, ListOp):
            for op in list_op.oplist:
                if not isinstance(op, PauliOp):
                    raise OpflowError(
                        "Cannot determine groups if any Operator in list_op is not "
                        f"`PauliOp`. E.g., {op} ({type(op)})"
                    )

        if isinstance(list_op, PauliSumOp):
            # Roundabout way of getting m.
            primitive = list_op.primitive
            m = int(log(primitive[0].to_matrix().shape[0], 2))
            #print(f'{m = }')
            #print(f'{primitive = }')
            #print(f'{len(primitive) = }')
            if len(primitive) == 4**m:
                groups = get_groups2(list_op, m)
                result = SummedOp(
                    [PauliSumOp(primitive[group], grouping_type="TPB") for group in groups.values()],
                    coeff=list_op.coeff,
                )

            else:
                groups = get_groups2(list_op, m)
                result = SummedOp(
                    [PauliSumOp(primitive[group], grouping_type="TPB") for group in groups.values()],
                    coeff=list_op.coeff,
                )
            return result
        
        group_ops: List[ListOp] = [
            list_op.__class__([list_op[idx] for idx in group], abelian=True)
            for group in groups.values()
        ]
        if len(group_ops) == 1:
            return group_ops[0].mul(list_op.coeff)
        return list_op.__class__(group_ops, coeff=list_op.coeff)
