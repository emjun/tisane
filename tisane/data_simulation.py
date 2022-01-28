import math
import os
import json
import csv
import struct
import pandas as pd
import numpy as np


class data_simulation:

    '''
    Providing a higher level of abstraction for generating dataframe
    '''



    '''
    Reads data from file at given path
    '''
    def read_data(self, filepath):
        return pd.read_csv(filepath)


    '''
    Generates data from given specification file
    arguments:
        data_spec: json file specifying column types and range
    '''
    def generate_data(self, cardinality, json_filepath):
        f = open(json_filepath)
        table_spec = json.load(f)
        structure_map, value_map = self.__create_variable_value_map(table_spec, cardinality)
        simulated_csv = self.__generate_csv(structure_map, value_map, json_filepath, cardinality)
        self.read_data(simulated_csv)

    def __create_variable_value_map(self, json_dict, cardinality):
        structure_map = {}
        value_map = {}
        for variable in json_dict:
            if "values" in json_dict[variable] and "distribution" in json_dict[variable]:
                raise Exception("Variable cannot have both, a values and range field.")
            
            if variable not in structure_map:
                structure_map[variable] = {}
                value_map[variable] = {}

            if "values" in json_dict[variable]:
                value_map[variable] = self.__from_given_values(json_dict[variable]["values"], cardinality)
            elif "range" in json_dict[variable]:
                dist = json_dict[variable]["distribution"] if "distribution" in json_dict[variable] else None
                variable_range = json_dict[variable]["range"]
                value_map[variable] = self.__generate_distribution_values(dist, cardinality, variable_range[0], variable_range[1])
            
            if "nested_variables" in json_dict[variable]:
                nested_map = json_dict[variable]["nested_variables"]
                sub_structure, sub_value = self.__create_variable_value_map(
                    nested_map, cardinality)
                structure_map[variable] = sub_structure
                value_map.update(sub_value)
            else:
                structure_map[variable] = {}
        return structure_map, value_map
    
    def __from_given_values(self, values, cardinality):
        while len(values) < cardinality:
            values.extend(values)
        return values

    def __generate_distribution_values(self, dist, size, lo, hi):
        result = []
        if dist is None:
            temp = np.arange(lo, hi + 1)
            length = len(temp)
            result = np.repeat(temp, math.ceil(size/length))
        elif dist == "normal":
            result = np.random.normal(size=size)
        elif dist == "random":
            result = np.random.randint(lo, hi + 1, size=size)
        return np.random.permutation(result)

    def __generate_csv(self, structure_map, value_map, json_filepath, cardinality):
        dir_path = os.path.dirname(json_filepath)
        result_path = os.path.join(dir_path, 'simulated.csv')
        f = open(result_path, 'w')
        writer = csv.writer(f)

        header_row = self.__build_header_row(structure_map)
        writer.writerow(header_row)
        value_rows = self.__build_value_rows(value_map, cardinality)
        writer.writerows(value_rows)
        return result_path

    def __build_value_rows(self, value_map, cardinality):
        rows = []
        for i in range(0, cardinality):
            row = []
            for var in value_map:
                row.append(value_map[var][i])
            rows.append(row)
        print(len(rows), ",", len(rows[0]))
        return rows

    def __build_header_row(self, structure_map):
        header = []
        for variable in structure_map:
            header.append(variable)
            sub_header = self.__build_header_row(structure_map[variable])
            header.extend(sub_header)
        return header        

if __name__ == '__main__':
    temp = data_simulation()
    filepath = "/Users/shreyashnigam/Desktop/plse/scripts/tisane_school/schools.json"
    temp.generate_data(100, filepath)
