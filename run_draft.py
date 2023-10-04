import gurobipy

gurobipy.setParam("TokenFile", "gurobi.lic")
model = gurobipy.model()

model.dispose()