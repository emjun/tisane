import tisane as ts
from tisane.main import check_design_ivs, check_design_dv

import unittest


class CheckTest(unittest.TestCase):
    def test_iv_causes_dv(self):
        u = ts.Unit("Unit")
        dv = u.numeric("DV")
        v1 = u.nominal("V1")
        v2 = u.nominal("V2")

        # Conceptual relationships
        v1.causes(dv)

        design = ts.Design(dv=dv, ivs=[v1, v2])

        error = False
        try:
            check_design_ivs(design)
        except:
            error = True

        self.assertTrue(error)

    def test_dv_causes_iv(self):
        u = ts.Unit("Unit")
        dv = u.numeric("DV")
        v1 = u.nominal("V1")
        v2 = u.nominal("V2")

        # Conceptual relationships
        v1.causes(dv)
        dv.causes(v2)

        design = ts.Design(dv=dv, ivs=[v1, v2])

        error = False
        try:
            check_design_dv(design)
        except:
            error = True

        self.assertTrue(error)
