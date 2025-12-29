# -*- coding: utf-8 -*-

import sympy
from ..salcs import (
    calc_salcs_projection,
    calc_salcs_func,
    _expand_irreducible,
    _angles_to_vectors,
)


def test_calc_salcs_projection():
    # ammonia hydrogens
    a, b, c = sympy.symbols('a b c')
    assert (calc_salcs_projection([a, b, c, a, b, c], 'c3v') ==
            [a + b + c, 0, a - b/2 - c/2])

    # trigonal bipyramidal
    a1, a2, e1, e2, e3 = sympy.symbols('a1, a2, e1, e2, e3')
    assert (calc_salcs_projection([e1, e2, e3, -e1, -e2, -e3, -e1,
                                   -e2, -e3, e1, e2, e3], 'd3h') ==
            [0, 0, 0, 0, e1 + e2 + e3, e1 - e2/2 - e3/2])
    assert (calc_salcs_projection([a1, a1, a1, -a2, -a2, -a2, -a2,
                                   -a2, -a2, a1, a1, a1], 'd3h') ==
            [a1 - a2, 0, 0, 0, a1 + a2, 0])

    # square planar s-orbitals
    a, b, c, d = sympy.symbols('a b c d')
    after_trans = [a, b, d, c, c, a, d, b, c, b, d, a, c, a, d, b]
    assert (calc_salcs_projection(after_trans, 'd4h') ==
            [a + b + c + d, 0, a - b + c - d, 0, 0, 0, 0, 0, 0, a - c])

    # benzene p-orbitals
    a, b, c, d, e, f = sympy.symbols('a b c d e f')
    after_trans = [a, b, f, c, e, d, -a, -c, -e, -b, -d, -f, -d, -c, -e, -b,
                   -f, -a, b, d, f, a, c, e]
    assert (calc_salcs_projection(after_trans, 'd6h') ==
            [0, 0, 0, a - b + c - d + e - f, a + b/2 - c/2 - d - e/2 + f/2,
             0, 0, a + b + c + d + e + f, 0, 0, 0,
             a - b/2 - c/2 + d - e/2 - f/2])

    # butadiene p-orbitals - inequivalent p-orbitals are treated separately
    a, b, c, d = sympy.symbols('a b c d')
    after_trans_outer = [a, -d, -a, d]
    after_trans_inner = [b, -c, -b, c]
    assert (calc_salcs_projection(after_trans_outer, 'c2v') ==
            [0, a - d, 0, a + d])
    assert (calc_salcs_projection(after_trans_inner, 'c2v') ==
            [0, b - c, 0, b + c])


def test_calc_salcs_func():
    # square planar
    a, b, c, d = sympy.symbols('a b c d')
    salc_true1 = [a + b + c + d, 0, a - b + c - d, 0, 0, 0, 0, 0, 0,
                  [a - c, b - d]]
    assert (calc_salcs_func([[1, 0, 0], [0, 1, 0], [-1, 0, 0], [0, -1, 0]],
                            'd4h', [a, b, c, d], mode='vector') == salc_true1)

    # trigonal bipyramidal - a is for axial and e is for equatorial
    a1, a2, e1, e2, e3 = sympy.symbols('a1, a2, e1, e2, e3')
    salc_true2 = [[e1 + e2 + e3, a1 + a2], 0,
                  [e1 - 0.5*e2 - 0.5*e3, e2 - e3, e1 - 0.5*e2 - 0.5*e3,
                   e2 - e3], 0, a1 - a2, 0]
    angles = [[0, 90], [120, 90], [240, 90], [0, 0], [0, 180]]
    assert (calc_salcs_func(angles, 'd3h', [e1, e2, e3, a1, a2], mode='angle')
           == salc_true2)

    # seesaw - such as SF4, a is for axial and e is for equatorial
    a1, a2, e1, e2 = sympy.symbols('a1 a2 e1 e2')
    salc_true3 = [[e1 + e2, a1 + a2, e1 + e2, e1 + e2], 0, a1 - a2,
                  [e1 - e2, e1 - e2]]
    assert (calc_salcs_func([[0, 90], [-180, 90], [90, 120], [-90, 120]],
                            'c2v', [a1, a2, e1, e2], mode='angle') ==
            salc_true3)

    # octahedral
    a, b, c, d, e, f = sympy.symbols('a b c d e f')
    salc_true4 = [a + b + c + d + e + f, 0,
                  [-0.5*a - 0.5*b - 0.5*c - 0.5*d + e + f, a - b + c - d],
                  0, 0, 0, 0, 0, [a - c, b - d, e - f], 0]
    oh_angle = calc_salcs_func([[0, 90], [90, 90], [180, 90], [270, 90],
                                [0, 0], [0, -180]], 'oh', [a, b, c, d, e, f],
                               mode='angle')
    oh_vector = calc_salcs_func([[1, 0, 0], [0, 1, 0], [-1, 0, 0], [0, -1, 0],
                                 [0, 0, 1], [0, 0, -1]], 'oh',
                                [a, b, c, d, e, f])
    assert oh_angle == salc_true4
    assert oh_vector == salc_true4


def test_expand_irreducible():
    assert _expand_irreducible([2, -1, 0], 'c3v') == [2, -1, -1, 0, 0, 0]


def test_angles_to_vectors():
    assert (_angles_to_vectors([[0, 90], [90, 90], [180, 90], [-90, 90]]) ==
            [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0],
             [0.0, -1.0, 0.0]])
