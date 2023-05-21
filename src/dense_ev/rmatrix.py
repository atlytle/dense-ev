#!/usr/bin/env python3
# Author: Andrew Lytle
# Nov 2022

# Copyright 2023 University of Illinois at Urbana-Champaign
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from math import log
from collections import defaultdict

import numpy as np
from numpy.linalg import eig
from numpy.random import normal
from scipy.stats import unitary_group

from qiskit.opflow.primitive_ops import PauliOp
from qiskit.quantum_info.operators import Pauli
from qiskit.opflow.list_ops.summed_op import SummedOp
from qiskit.opflow.primitive_ops.pauli_sum_op import PauliSumOp
from qiskit.opflow.converters import AbelianGrouper

#from qiskit.opflow.converters.pauli_basis_change import PauliBasisChange
#from qiskit.opflow.state_fns.state_fn import StateFn

from dense_ev.decompose_pauli import to_pauli_vec
from psfam.pauli_organizer import PauliOrganizer

def random_evals(N):
    "List of Gaussian distributed numbers [(0,1),...]."
    vals = []
    for i in range(N):
        vals.append(normal())
    return vals

def dot_all(Ms):
    "Dot product of [M1, M2, ...]"
    res = np.identity(Ms[0].shape[0])
    for M in Ms[::-1]:
        res = np.dot(M, res)
    return res

def hc(M):
    "Hermitian conjugate of M."
    return M.conj().T

def random_H(N):
    "Random NxN Hermitian matrix."
    evs = random_evals(N)
    D = np.diag(evs)
    U = unitary_group.rvs(N)
    H = dot_all([U, D, hc(U)])
    return H

def test_random_H(m):
    N=pow(2,m)
    evs = random_evals(N)
    D = np.diag(evs)
    U = unitary_group.rvs(N)
    H = dot_all([U, D, hc(U)])
    vals, vecs = eig(H)

    print(evs)
    print(D)
    print(vals)

def array_to_Op(Hmat):
    "Convert numpy matrix to qiskit Operator type object."

    N = Hmat.shape[0]
    m = log(N, 2)
    assert m == int(m)
    m = int(m)

    pauli_vec = to_pauli_vec(Hmat)
    #print(pauli_vec)
    #print(len(pauli_vec))
    
    H_op=PauliOp(Pauli('I'*m), 0.0)
    #print(type(H_op))
    for pauli_string in pauli_vec.keys():
        coefficient = pauli_vec[pauli_string]
        #if(abs(coefficient) > 0.0001 ):
        H_op += PauliOp(Pauli(pauli_string), coefficient)
    #print(type(H_op))
    return H_op

def get_groups(m):
    """Specification of Pauli string families suitable for use in Qiskit.
    
    Args: 
        int m: Number of qubits
    
    Returns:
        defaultdict<list> {1: [i, j, k,...], 2: [l, m, n,...], ...}
        where [i, j, k,...] are integers specifying the Pauli operators
        in the family, according to the internal Qiskit ordering
        (e.g. id_list below.)

    Note: Currently function generates a random H matrix to obtain 
    the default qiskit operator ordering (H.primitive). This
    can probably be rewritten so that this isn't necessary.
    """
    N = 2**m
    PO = PauliOrganizer(m)

    # Long way to get primitive elements..
    Hmat = random_H(N)
    H = array_to_Op(Hmat)
    primitive = H.primitive
    #print('primitive:', primitive)
    #print('paulis:', primitive.paulis)
    
    # How stored in Op objects.
    '''
    id_list = \
    ['III', 'IIZ', 'IIX', 'IIY', 'IZI', 'IZZ', 'IZX', 'IZY', 'IXI', 'IXZ', 'IXX', 'IXY', 
    'IYI', 'IYZ', 'IYX', 'IYY', 'ZII', 'ZIZ', 'ZIX', 'ZIY', 'ZZI', 'ZZZ', 'ZZX', 'ZZY', 
    'ZXI', 'ZXZ', 'ZXX', 'ZXY', 'ZYI', 'ZYZ', 'ZYX', 'ZYY', 'XII', 'XIZ', 'XIX', 'XIY', 
    'XZI', 'XZZ', 'XZX', 'XZY', 'XXI', 'XXZ', 'XXX', 'XXY', 'XYI', 'XYZ', 'XYX', 'XYY', 
    'YII', 'YIZ', 'YIX', 'YIY', 'YZI', 'YZZ', 'YZX', 'YZY', 'YXI', 'YXZ', 'YXX', 'YXY', 
    'YYI', 'YYZ', 'YYX', 'YYY']
    '''
    # Will primitive.paulis include the full set irrespective of H?
    id_list = [str(x) for x in primitive.paulis]
    id_dict = { id_list[x]: x for x in range(len(id_list))}
    #print('id_dict:', id_dict)

    res = []
    for family in PO.f:
        #print(family.to_string())
        fam_ids = []
        for op in family.to_string():
            fam_ids.append(id_dict[op])
        res.append(fam_ids)
    # Feb 25, the following line isn't needed anymore?
    #res[-1].append(0)  # Add the identity operator to the last family.

    groups = defaultdict(list)
    groups = {i: res[i] for i in range(len(res))}
    return groups

def get_groups2(H, m):
    """Specification of Pauli string families suitable for use in Qiskit.
    
    Args: 
        int m: Number of qubits
    
    Returns:
        defaultdict<list> {1: [i, j, k,...], 2: [l, m, n,...], ...}
        where [i, j, k,...] are integers specifying the Pauli operators
        in the family, according to the internal Qiskit ordering
        (e.g. id_list below.)

    Note: Currently function generates a random H matrix to obtain 
    the default qiskit operator ordering (H.primitive). This
    can probably be rewritten so that this isn't necessary.
    """
    N = 2**m
    PO = PauliOrganizer(m)

    # Long way to get primitive elements..
    #Hmat = random_H(N)
    #H = array_to_Op_filter(Hmat)
    primitive = H.primitive
    #print('primitive:', primitive)
    #print('paulis:', primitive.paulis)
    
    # How stored in Op objects.
    '''
    id_list = \
    ['III', 'IIZ', 'IIX', 'IIY', 'IZI', 'IZZ', 'IZX', 'IZY', 'IXI', 'IXZ', 'IXX', 'IXY', 
    'IYI', 'IYZ', 'IYX', 'IYY', 'ZII', 'ZIZ', 'ZIX', 'ZIY', 'ZZI', 'ZZZ', 'ZZX', 'ZZY', 
    'ZXI', 'ZXZ', 'ZXX', 'ZXY', 'ZYI', 'ZYZ', 'ZYX', 'ZYY', 'XII', 'XIZ', 'XIX', 'XIY', 
    'XZI', 'XZZ', 'XZX', 'XZY', 'XXI', 'XXZ', 'XXX', 'XXY', 'XYI', 'XYZ', 'XYX', 'XYY', 
    'YII', 'YIZ', 'YIX', 'YIY', 'YZI', 'YZZ', 'YZX', 'YZY', 'YXI', 'YXZ', 'YXX', 'YXY', 
    'YYI', 'YYZ', 'YYX', 'YYY']
    '''
    # Will primitive.paulis include the full set irrespective of H?
    id_list = [str(x) for x in primitive.paulis]
    id_dict = { id_list[x]: x for x in range(len(id_list))}
    #print('id_dict:', id_dict)

    res = []
    for family in PO.f:
        #print(family.to_string())
        fam_ids = []
        for op in family.to_string():
            try:
                fam_ids.append(id_dict[op])
            except KeyError:
                continue
        res.append(fam_ids)
    # Feb 25, the following line isn't needed anymore?
    #res[-1].append(0)  # Add the identity operator to the last family.

    groups = defaultdict(list)
    groups = {i: res[i] for i in range(len(res)) if res[i]}
    return groups

def array_to_SummedOp(Hmat):
    "Convert numpy matrix to SummedOp grouped into Pauli-string families."
    N = Hmat.shape[0]
    m = log(N, 2)
    assert m == int(m)
    m = int(m)
    #PO = PauliOrganizer(m)

    H = array_to_Op(Hmat)
    primitive = H.primitive
    #print('primitive:', primitive)
    #print('paulis:', primitive.paulis)
    
    groups = get_groups(m)

    result = SummedOp(
        [PauliSumOp(primitive[group], grouping_type="TPB") for group in groups.values()],
        coeff=1)

    #print('result:', result)
    #print('len(result):', len(result))

    return result

def get_Op(Hmat, optype):
    "Qiskit operators from matrix array."
    if optype == 'naive':
        return array_to_Op(Hmat)
    elif optype == 'abelian':
        grouper = AbelianGrouper()
        H = array_to_Op(Hmat)
        return grouper.convert(H)
    elif optype == 'new':
        return array_to_SummedOp(Hmat)
    else:
        msg = f'optype {optype} not recognized [naive, abelian, new].'
        raise ValueError(msg)

if __name__ == '__main__':
    #print(get_groups(2))
    Hmat = random_H(8)
    #print(array_to_SummedOp(Hmat))
    print(get_Op(Hmat, 'abelian'))
    
