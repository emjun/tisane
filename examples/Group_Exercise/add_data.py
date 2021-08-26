"""
Script to add age to the dataset
"""
import random 
import pandas as pd 

df = pd.read_csv("/Users/emjun/Git/tisane/examples/Group_Exercise/exercise_group.csv")

random_ages = random.choices(range(18,90, 1), k=386)

df["age"] = random_ages

df.to_csv('/Users/emjun/Git/tisane/examples/Group_Exercise/exercise_group_age_added.csv')
