"""A machine learning module for the simulation.

The idea of this module is to enable optimisation of some model
constants so that the model can approximate real data in the best
possible way.

A main assumption is that an ideal model can capture how a system work and
it is a perfect function of the previous step.

Consider the model :math:`\\mathcal{M}` that takes inputs from
:math:`\\mathcal{X}` to :math:`\\mathcal{Y}`.
ML training variables are constants (otherwise you can't optimize them)
 in the model that one wants to optimize.
:math:`x_{train}`.
ML predicted variables :math:`y_{pred} = \\mathcal{M}(x_{train})`
are variables that the model calculates and
that change at each step.
ML target variables  :math:`y_{target}`
come from real data and correspond to the data that
the model tries to approximate.
An error metric :math:`err(y_{target}, y_{pred})` calculate the error
between the predicted and target values.
The goal of the ML algorithm is to find :math:`x_{train}` that
 minimise the :math:`min_{x_{train}} err(y_{target}, y_{pred})`
in other words,
 the goal is to find the model parameters such that the model
 approximate the real data in the best possible way.
 :math:`x_{best} = argmin_{x_{train}} err(y_{target}, y_{pred})`

The method that can be used to solve that are various and it is hard
to know which one is the best. The main unkonws are which is the error
metrics and which model we use for solving this problem.

The machine learning manager will listen to the model steps.
At every step it will record the :math:`x` that were used before
the update and the :math:`y_{pred}` is also registerd.
This can help building a dataset for then optimising the x variables.

.. warning::
    This module might not be compatible with some modding that changes
    the values of variables. We  need to investigate how compatiblity
    could be ensured.
"""
