import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# ----------------------------
# Weibull cross section model
# ----------------------------
def weibull(LET, LET_th, sigma_sat, s, w):
    LET = np.array(LET, dtype=float)
    sigma = np.zeros_like(LET)

    idx = LET >= LET_th
    sigma[idx] = sigma_sat * (1.0 - np.exp(-((LET[idx] - LET_th) / w) ** s))
    return sigma

# -----------------------------------------
# Log-space model for aggressive knee fitting
# -----------------------------------------
def log_weibull(LET, LET_th, sigma_sat, s, w):
    eps = 1e-30  # avoids log(0)
    return np.log10(weibull(LET, LET_th, sigma_sat, s, w) + eps)

# ----------------------------
# Your data
# ----------------------------
LET = np.array([0.89, 1.64, 7, 16, 25])  # MeV·cm²/mg
#sigma = np.array([1.267e-7, 2.72e-6, 6.36e-5, 2.8e-4, 2.3e-4])  # cm²/device
sigma = np.array([4.73E-08 , 2.72e-6, 6.36e-5, 2.8e-4, 2.3e-4])  # cm²/device
log_sigma = np.log10(sigma)




# -----------------------------------------
# AGGRESSIVE WEIGHTING
# -----------------------------------------
# smaller sigma => higher weight
p = 2.0  # try 1.5, 2.0, 2.5, 3.0
sigma_log_err = LET**p
sigma_log_err /= np.min(sigma_log_err)  # normalize

# -----------------------------------------
# Initial guesses
# -----------------------------------------
p0 = [
    1.0,        # LET_th
    max(sigma), # sigma_sat
    3.0,        # s
    8.0         # w
]

# -----------------------------------------
# Bounds
# -----------------------------------------
bounds = (
    [0.0, 0.0, 0.1, 0.01],
    [50.0, 1e-2, 20.0, 200.0]
)

# -----------------------------------------
# Fit in log space with LET-biased weights
# -----------------------------------------
popt, pcov = curve_fit(
    log_weibull,
    LET,
    log_sigma,
    p0=p0,
    bounds=bounds,
    sigma=sigma_log_err,
    absolute_sigma=False,
    maxfev=500000
)

LET_th, sigma_sat, s, w = popt

print("\nAGGRESSIVE WEIGHTED (log-space) Weibull fit:")
print(f"LET_th    = {LET_th:.4f} MeV·cm²/mg")
print(f"sigma_sat = {sigma_sat:.4e} cm²/device")
print(f"s         = {s:.4f}")
print(f"w         = {w:.4f} MeV·cm²/mg")

# -----------------------------------------
# Plot in linear sigma, log y-axis
# -----------------------------------------
LET_fit = np.linspace(0, 30, 800)
sigma_fit = weibull(LET_fit, *popt)

plt.figure(figsize=(7, 5))
plt.semilogy(LET, sigma, "o", label="Data")
plt.semilogy(LET_fit, sigma_fit, "-", label=f"Aggressive fit (p={p})")
plt.xlabel("LET (MeV·cm²/mg)")
plt.ylabel("Cross section (cm²/device)")
plt.grid(True, which="both")
plt.legend()
plt.tight_layout()
plt.show()

# -----------------------------------------
# Residuals in log space
# -----------------------------------------
pred_log_sigma = log_weibull(LET, *popt)
resid = log_sigma - pred_log_sigma

print("\nLog-space residuals (data - fit):")
for L, r in zip(LET, resid):
    print(f"LET={L:6.2f}  residual={r:+.4f} decades")
