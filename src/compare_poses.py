import pandas as pd

real_poses = pd.read_csv("planets2.csv")
simulated_poses = pd.read_csv("planets.csv")

print(real_poses.head())
print(simulated_poses.head())

