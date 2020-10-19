#!/usr/bin/env python
"""Digits of PI Calculator

Copyright 2017 Louis Huemiller

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Calculates the value of PI, to a specified number of digits (default 100).
Value is calculated by starting with a 4-sided regular polygon (a square)
within a circle with a radius of 1.  It then iteratively doubles the number
of sides, until there are enough sides to calculate PI to the requested
number of digits.  Calculates approximately 0.6 decimal digits of PI per
iteration.

  Command-line Options:
      --digits       - Digits of PI to be calculated (default: 100)
      --digits_guard - Number of additional guard digits.  Used to handle
                       rounding within calculation (default: 100).
"""

from __future__ import print_function
from __future__ import division

import argparse
import decimal
from decimal import Decimal

numerically_unstable_msg = '''
---- Numerically Unstable ---
Use --digits_guard to increase the number of guard digits.
'''

class right_triangle(object):
    @staticmethod
    def other_side(s1, hypot = Decimal(1.0)):
        '''
        Calculates and returns the length of the other side of
        a right-triangle, given the length of a side and the length
        of the hypotenuse.
        '''
        squared_difference = (hypot * hypot) - (s1 * s1)
        return pow(squared_difference, Decimal(0.5))  # Square root

    @staticmethod
    def half_angle(s1, hypot = Decimal(1.0)):
        '''
        Given the length of the hypotenuse plus a side opposed to a non-right
        angle, calculates and returns the length of the side if the non-right
        angle was halved.
        '''
        f = s1 * (Decimal(1) / hypot)
        f = pow((Decimal(1.0) - right_triangle.other_side(f))
                / Decimal(2.0), Decimal(0.5))
        return f * hypot

def num_digits_in_common(val1, val2):
    '''
    Calculates and returns the number of digits in common between
    two numbers of type decimal.  Returns 0 if the first digit, signs,
    or exponent don't match.
    '''
    t1 = val1.as_tuple()
    t2 = val2.as_tuple()
    if t1.sign != t2.sign: return 0
    if t1.exponent != t2.exponent: return 0

    for n1 in range(len(t1.digits)):
        if n1 >= len(t2.digits): break
        if t1.digits[n1] != t2.digits[n1]: break

    return n1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='''
        Calculates the value of PI, to a specified number of digits.
        Iteratively uses a trigonometric half-angle identity, to
        determine the circumference of a polygon with twice the
        number of sides as the previous iteration.
        ''')
    parser.add_argument('-d', '--digits', type=int, default=100,
            help='Number of PI digits to calculate')
    parser.add_argument('-g', '--digits_guard', type=int, default=100,
            help='Number of guard digits, to handle rounding')
    args = parser.parse_args()

    decimal.getcontext().prec = args.digits + args.digits_guard

    # Start with a 4-side regular polygon, a square.
    f = Decimal(1.0)
    sides = Decimal(4.0)

    num_digits = 0
    prev_num_digits = 0
    iteration = 0

    while num_digits < args.digits:
        # Double the number of sides.
        f = right_triangle.half_angle(f);
        sides *= 2

        # Calculate a lower and upper bound for the value of PI.
        pi_lower = (f * sides) / Decimal(2)
        pi_upper = (((Decimal(1) / right_triangle.other_side(f)) * f)
                * sides) / Decimal(2)

        # Determine and display the number of leading digits in common between
        # the lower and upper bounds.
        num_digits = num_digits_in_common(pi_lower, pi_upper)
        print('%8i %10s %.*s'
                % (iteration, num_digits, num_digits + 1, pi_lower) )

        # Still numerically stable?
        if num_digits < prev_num_digits:
            print(numerically_unstable_msg)
            raise SystemExit(1)
        prev_num_digits = num_digits

        iteration += 1
