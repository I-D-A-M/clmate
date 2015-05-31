# -*- coding: utf-8 -*-
import pytest
from ..helpers import mean, median, percentage_marks, colourise


class Test_median():
    def test_even_number_of_values_ordered(self):
        assert median([1, 2, 3, 4]) == 2

    def test_even_number_of_values_unordered(self):
        assert median([1, 9, 2, 4]) == 3

    def test_odd_number_of_values_ordered(self):
        assert median([1, 2, 3, 4, 5]) == 3

    def test_odd_number_of_values_unordered(self):
        assert median([1, 4, 2, 9, 17]) == 4

    def test_not_a_list(self):
        with pytest.raises(AssertionError):
            median('This is not a list!') == 'Success'


class Test_mean():
    def test_even_number_of_values_ordered(self):
        assert mean([1, 2, 3, 4]) == 2.5

    def test_odd_number_of_values_ordered(self):
        assert mean([1, 2, 3, 4, 5]) == 3

    def test_not_a_list(self):
        with pytest.raises(AssertionError):
            mean('This is not a list!')

    def test_non_numeric_list(self):
        with pytest.raises(TypeError):
            mean(['bob', 'sally', 'jeff', ])


class Test_percentage_marks():
    def test_full_marks(self):
        assert percentage_marks(100, 100) == 100.00

    def test_no_marks(self):
        assert percentage_marks(0, 100) == 0.00

    def test_non_numeric(self):
        with pytest.raises(TypeError):
            percentage_marks('5', 100)


class Test_colourise():
    def test_RYG_boundaries(self):
        assert colourise(59.9) == 'Red'
        assert colourise(60) == 'Orange'
        assert colourise(90) == 'Green'

    def test_0_and_100(self):
        assert colourise(0) == 'Red'
        assert colourise(100) == 'Green'

    def test_negative_input(self):
        with pytest.raises(AssertionError):
            colourise(-1)

    def test_input_over_100(self):
        with pytest.raises(AssertionError):
            colourise(9001)
