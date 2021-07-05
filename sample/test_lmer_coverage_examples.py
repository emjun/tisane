import tisane as ts

import unittest


# LMER formula -> Tisane StatisticalModel -> Tisane Study Design (+ steps)
class LmerCoverageExamples(unittest.TestCase):
    def test_random_intercept(self):
        pass

    def test_random_intercept_with_offset_(self):
        pass

    def test_nesting(self):
        pass

    def test_two_random_intercepts(self):
        pass

    def test_correlated_random_slope_intercept(self):
        pass


class DataForTests:
    sd = ts.Design(
        # https://rpsychologist.com/r-guide-longitudinal-lme-lmer
    )
