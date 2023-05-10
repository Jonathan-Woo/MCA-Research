#%%
from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.pyplot as plt
#%%
a = np.linspace(1,5,5).reshape(-1,1)
b = np.linspace(3,7,5).reshape(-1,1)
# %%
model = LinearRegression()

model.fit(a, b)
# %%
plt.plot(a, model.predict(a))
# %%
