"""Test if I can run pysd in parallel, using vectorisation."""

# %%
import pysd

# %%
model1 = pysd.read_vensim("teacup.mdl")
df = model1.run(final_time=50)


# %%
