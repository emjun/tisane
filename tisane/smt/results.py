from typing import List

class StatisticalTestResult(object): 
    name: str
    test_statistic_name: str
    test_statistic_value: float
    p_value: float 

    def __init__(self, name: str, test_statistic_name: str, test_statistic_value: float, p_value: float): 
        self.name = name
        self.test_statistic_name = test_statistic_name
        self.test_statistic_value = test_statistic_value
        self.p_value = p_value

class AllStatisticalResults(object):

    statistics_models: List[StatisticalTestResult]
    
    def __init__(self):
        self.statistics_models = list()