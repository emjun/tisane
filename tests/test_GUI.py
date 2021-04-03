import tisane as ts
from tisane.smt.input_interface import InputInterface

import unittest
import dash_html_components as html
import dash_bootstrap_components as dbc

class GUITest(unittest.TestCase):
    def test_get_random_effects_values_from_table(self):
        pass
        # rs_badge = dbc.Badge("Random slope", pill=True, color="primary", className="mr-1", id=f'RandomSlope(test)')
        # ri_badge = dbc.Badge("Random intercept", pill=True, color="info", className="mr-1", id=f'RandomIntercept(test)')

        # row = html.Tr(
        #             children=[html.Td(html.P(children=[rs_badge, ri_badge]))],
        #             hidden=False,
        #             id=f'test_random_effects'
        #         )

        # table_body = [html.Tbody(children=row)]
        # table = dbc.Table(children=table_body, striped=True, bordered=False, id='random_effects_table')

        # app = InputInterface()
        # app.get_random_effects_values_from_table(table_body)


