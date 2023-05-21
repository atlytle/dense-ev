#!/usr/bin/env python3
# Authors: Nouman Butt, Andrew Lytle

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

import numpy as np
import scipy.sparse as sp
import itertools, functools
#from e1plus import get_eigenvalues

op_I = sp.eye(2)
op_Z = sp.dia_matrix([[1,0],[0,-1]])
op_X = sp.dia_matrix([[0,1],[1,0]])
op_Y = -1j * op_Z @ op_X

C1 = [[1,0],[0,0]]
C2 = [[0,1],[0,0]]
C3 = [[0,0],[1,0]]
C4 = [[0,0],[0,1]]



C_ops = { "C1" : C1, "C2" :C2, "C3": C3, "C4" : C4 }
pauli_ops = { "I" : op_I, "Z" : op_Z, "X": op_X, "Y" : op_Y }

# def pauli_strings(num_qubits):
#     """Generate all Pauli strings with num_qubits.

#     Args: 
#         int, number of qubits
#     Returns:
#         Generator of Pauli strings, as tensor products.
#     """
#     for pauli_string in itertools.product(pauli_ops.keys(), repeat = num_qubits):
#         # construct this pauli string as a matrix
#         ops = [pauli_ops[tag] for tag in pauli_string]
#         op = functools.reduce(sp.kron, ops)
#         yield op.toarray()

def sp_kron_dok(mat_A, mat_B): 
    """Kronecker (tensor) product of two sparse matrices.
    
    Args:
        mat_A, mat_B: 2d numpy arrays
    Returns:
        Sparse matrix in "dictionary of keys" format (to eliminate zeros)
    """
    return sp.kron(mat_A, mat_B, format = "dok")

def to_pauli_vec(mat):
    """Pauli string decomposition of a matrix.

    Args:
        2d numpy array, mat
    Returns:
        Dictionary pauli_vec, e.g. {'XX': 0.5, 'XY': 0.5}
    """
    pauli_vec = {} # the dictionary we are saving

    mat_vec = np.array(mat).ravel()
    num_qubits = int(np.log2(np.sqrt(mat_vec.size)))

    for pauli_string in itertools.product(pauli_ops.keys(), repeat = num_qubits):
        # construct this pauli string as a matrix
        ops = [ pauli_ops[tag] for tag in pauli_string ]
        op = functools.reduce(sp_kron_dok, ops)

        # compute an inner product, same as tr(A @ B) but faster
        op_vec = op.transpose().reshape((1, 4**num_qubits))
        coefficient = (op_vec * mat_vec).sum() / 2**num_qubits
        pauli_vec["".join(pauli_string)] = coefficient

    return pauli_vec

def pauli_string_to_mat(pauli_string):
    """Numpy array representing pauli_string.
    
    Args: pauli_string e.g. 'XYZ'
    Returns: 
        Numpy array of shape (2**m, 2**m) representing pauli_string as 
        a tensor product.
    """
    ops_primitive = [pauli_ops[tag] for tag in pauli_string]
    op = functools.reduce(sp.kron, ops_primitive)
    return op.toarray()

# See also gen_random_pauli_dict(m) in Psfam_documentation.ipynb

def from_pauli_vec(pauli_vec):
    """Numpy array/matrix from dictionary of Pauli strings.

    Args:
        pauli_vec: Dictionary with Pauli string decomposition, 
        e.g. {'YZ': 1.0, 'XY': 2.0}.
    Returns:
        Numpy array corresponding to matrix specified by pauli_vec.
    """
    m = len(list(pauli_vec.keys())[0])
    result = np.zeros((2**m, 2**m), dtype='complex128')
    for string, coeff in pauli_vec.items():
        result += coeff*pauli_string_to_mat(string)
    return result

def to_C_vec(mat):
    C_vec = {} # the dictionary we are saving

    mat_vec = np.array(mat).ravel()
    num_qubits = int(np.log2(np.sqrt(mat_vec.size)))

    for C_string in itertools.product(C_ops.keys(), repeat = num_qubits):
        # construct this pauli string as a matrix
        ops = [ C_ops[tag] for tag in C_string ]
        op = functools.reduce(sp_kron_dok, ops)

        # compute an inner product, same as tr(A @ B) but faster
        op_vec = op.reshape((1,4**num_qubits))
        coefficient = ( op_vec * mat_vec ).sum() / 2**num_qubits
        if coefficient != 0:
            C_vec["".join(C_string)] = coefficient

    return C_vec


def test():
    mat = [[1,0,0,0],[0,0,0,1],[0,1,0,0],[0,1,0,0]] # for example...
    print(to_pauli_vec(mat))
    print(sp_kron_dok(mat, mat))

    #for ps in pauli_strings(1):
    #    print(ps)

    print()
    #pauli_vec = {'XY': 1.0, 'ZZ': 1.0}
    pauli_vec = {'Y': 1.0}
    matrix = from_pauli_vec(pauli_vec)
    print(matrix)
    print(to_pauli_vec(matrix))

    print(pauli_string_to_mat('Y'))
    print(op_Y.toarray())

if __name__ == "__main__":
    test()
