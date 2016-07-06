from __future__ import division
import numpy as np
import numpy.random as npr
import matplotlib.pyplot as plt

from pybasicbayes.distributions import Regression, AutoRegression
from pybasicbayes.util.text import progprint_xrange

from pylds.models import LDS, DefaultLDS

npr.seed(0)


#########################
#  set some parameters  #
#########################

p = 1
n = 2
d = 1
T = 2000

mu_init = np.array([0.,1.])
sigma_init = 0.01*np.eye(2)

A = 0.99*np.array([[np.cos(np.pi/24), -np.sin(np.pi/24)],
                   [np.sin(np.pi/24),  np.cos(np.pi/24)]])
B = np.ones((n,d))
sigma_states = 0.01*np.eye(2)

C = np.array([[10.,0.]])
D = np.zeros((p,d))
sigma_obs = 0.01*np.eye(1)

###################
#  generate data  #
###################

truemodel = LDS(
    dynamics_distn=AutoRegression(A=np.hstack((A,B)), sigma=sigma_states),
    emission_distn=Regression(A=np.hstack((C,D)), sigma=sigma_obs))

inputs = np.random.randn(T,d)
data, stateseq = truemodel.generate(T, inputs=inputs)


###############
#  fit model  #
###############

def update(model):
    model.resample_model()
    return model.log_likelihood()

model = LDS(
    dynamics_distn=Regression(nu_0=n + 2, S_0=n * np.eye(n),
                              M_0=np.zeros((n, n)), K_0=n*np.eye(n)),
    emission_distn=Regression(nu_0=p+1, S_0=p*np.eye(p),
                              M_0=np.zeros((p, n)), K_0=n*np.eye(n)))
model.add_data(data, inputs=None)

affinemodel = LDS(
    dynamics_distn=Regression(nu_0=n + 2, S_0=n * np.eye(n),
                              M_0=np.zeros((n, n+d)), K_0=(n+d) * np.eye(n+d)),
    emission_distn=Regression(nu_0=p+1, S_0=p*np.eye(p),
                              M_0=np.zeros((p, n+d)), K_0=(n+d)*np.eye(n+d)))
affinemodel.add_data(data, inputs=inputs)


# model = DefaultLDS(n=2,p=data.shape[1]).add_data(data)
lls = [update(model) for i in progprint_xrange(100)]
affine_lls = [update(affinemodel) for i in progprint_xrange(100)]

plt.figure(figsize=(3,4))
plt.plot(lls)
plt.plot(affine_lls)
plt.xlabel('iteration')
plt.ylabel('log likelihood')


################
#  predicting  #
################

# Npredict = 100
# prediction_seed = data[:1700]

# predictions = model.sample_predictions(
#     prediction_seed, Npredict, obs_noise=False)
#
# plt.figure()
# plt.plot(data, 'b-')
# plt.plot(prediction_seed.shape[0] + np.arange(Npredict), predictions, 'r--')
# plt.xlabel('time index')
# plt.ylabel('prediction')

plt.show()
