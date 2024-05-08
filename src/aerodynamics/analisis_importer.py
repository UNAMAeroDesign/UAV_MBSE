import numpy as np
import pandas as pd


class OpPoint:
    def __init__(self):
        self.distributions = []

    def read_file(self, op_point_file):
        with open(op_point_file, "r") as f:
            lines = f.readlines()

        # Store every index of empty lines
        sep = [i for i, line in enumerate(lines) if line == "\n"]
        # Well use this names as defaults to identify diferent sets of distributions:
        # WARNING: The code will fail if the dafult names were modified.
        table_names = ["Main Wing", "Elevator", "Fin", "Second Wing2"]

        # Read all the file parameters
        param_lines = lines[sep[0] + 1 : sep[1]]
        self.plane = param_lines[0].rstrip()
        parameters = {}
        for line in param_lines:
            parts = line.rstrip().replace("°", "").split()

            for i, part in enumerate(parts):
                if part == "=":
                    parameters[parts[i - 1]] = float(parts[i + 1])
        self.v = parameters["QInf"]
        self.alpha = parameters["Alpha"]
        self.beta = parameters["Beta"]
        self.phi = parameters["Phi"]
        self.parameters = parameters

        # Store the beggining line and end of each table in a list to slice
        intervals = [
            [sep[i] + 1, sep[i + 1]]
            for i in range(len(sep) - 1)
            if any(
                [
                    (line.rstrip("\n") in table_names)
                    for line in lines[sep[i] : sep[i + 1]]
                ]
            )
        ]

        for interval in intervals:
            # Slice file
            table_lines = lines[interval[0] : interval[1]]
            # First line will have name stored
            name = table_lines.pop(0).rstrip("\n")
            # headers
            headers = table_lines.pop(0).split()
            data_lines = table_lines
            data = np.array([[float(n) for n in line.split()] for line in data_lines])
            df_OpPoint = pd.DataFrame(data, columns=headers)
            distribution = SpanDistribution(name, df_OpPoint)
            distribution.calculate_forces(v=self.v, alpha=self.alpha)

            self.add_distribution(distribution)

    def add_distribution(self, distribution):
        self.distributions.append(distribution)


class SpanDistribution:

    def __init__(self, name, df):
        self.name = name
        self.df = df

    def __repr__(self):
        return self.name + " spanwise aerodynamic distribution"

    def calculate_forces(self, v=16.0, alpha=0, rho=1.225):

        df = self.df.copy(deep=False)
        df.loc[:, "dy"] = df["y-span"].diff()
        # Saving the positive part of distirbution
        dist = df[df["y-span"] >= 0].copy(deep=True)
        dist["dA"] = dist["dy"] * dist["Chord"]
        dist["Cd"] = dist["PCd"] + dist["ICd"]
        # Dynamic Pressure from input parameters
        q = 0.5 * rho * v**2
        dist["dL"] = q * dist["dA"] * dist["Cl"]
        dist["dD"] = q * dist["dA"] * dist["Cd"]
        # Strip Moment?
        dist["dM"] = q * dist["dA"] * dist["Chord"]

        self.df = dist
