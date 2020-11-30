import tisane as ts
from tisane.variable import NominalVariable, OrdinalVariable, NumericVariable

import unittest
# from importlib import reload


class ConceptTests(unittest.TestCase): 
    # def setUp(self): 
    #     reload(ts.main)

    def test_ctor(self): 
        concepts = list()
        for con in DataForTests.concepts_to_define:
            concepts.append(ts.Concept(con['name']))
    
        # ASSERT
        self.assertEqual(len(concepts), 3)
        for i in range(len(DataForTests.concepts_to_define)):
            self.assertEqual(concepts[i].name, DataForTests.concepts_to_define[i]['name'])

    def test_specify_data_vars_null(self): 
        concepts = list()
        for con in DataForTests.concepts_to_define:
            concepts.append(ts.Concept(con['name']))
        
        for i in range(len(DataForTests.concepts_to_define)):
            con = concepts[i]
            con.specifyData(dtype=DataForTests.concepts_to_define[i]["data type"])

        # ASSERT
        self.assertTrue(isinstance(concepts[0].variable, NominalVariable))
        self.assertIsNone(concepts[0].data())
        self.assertTrue(isinstance(concepts[1].variable, OrdinalVariable))
        self.assertIsNone(concepts[1].data())
        self.assertTrue(isinstance(concepts[2].variable, NumericVariable))
        self.assertIsNone(concepts[2].data())

    def test_specify_data_vars(self): 
        concepts = list()
        for con in DataForTests.concepts_to_define:
            concepts.append(ts.Concept(con['name']))
        
        for i in range(len(DataForTests.concepts_to_define)):
            con = concepts[i]
            data_type = DataForTests.concepts_to_define[i]["data type"]
            data = DataForTests.concepts_to_define[i]["data"]
            
            if data_type == "ordinal": 
                ordered_cat = DataForTests.concepts_to_define[i]["ordered_categories"]
                con.specifyData(dtype=data_type, order=ordered_cat, data=data)
            else: 
                con.specifyData(dtype=data_type, data=data)

        # ASSERT
        self.assertTrue(isinstance(concepts[0].variable, NominalVariable))
        self.assertEqual(concepts[0].data(), DataForTests.concepts_to_define[0]["data"])
        self.assertTrue(isinstance(concepts[1].variable, OrdinalVariable))
        self.assertEqual(concepts[1].data(), DataForTests.concepts_to_define[1]["data"])
        self.assertEqual(concepts[1].getVariable().ordered_cat, DataForTests.concepts_to_define[1]["ordered_categories"])
        self.assertTrue(isinstance(concepts[2].variable, NumericVariable))
        self.assertEqual(concepts[2].data(), DataForTests.concepts_to_define[2]["data"])

    def test_addData(self): 
        pass


class DataForTests:
    concepts_to_define = [
        {"name": "NominalT", "data type": "nominal", "categories": ["Nominal0"], "data": ["Val1", "Val2", "Val3"]},
        {"name": "OrdinalT", "data type": "ordinal", "ordered_categories": ["Ordinal1", "Ordinal2", "Ordinal3"], "data": ["Ordinal2", "Ordinal1", "Ordinal3"]},
        {"name": "NumericT", "data type": "numeric", "data": [1, 2, 3]},
    ]        