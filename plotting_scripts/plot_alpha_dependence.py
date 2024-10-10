import matplotlib.pyplot as plt
import numpy as np
import mplhep as hep

# Define the range of x
alpha = np.linspace(0, 1, 100)

# Define the functions
scale_Ybb = 0.0973 * alpha
scale_Ytt = 0.9027 * (1 - alpha)

plt.style.use(hep.style.CMS)

# Create the plot
# plt.plot(alpha, scale_Ybb, label=r'0.0627*\alpha_{Y(bb)}')
# plt.plot(alpha, scale_Ytt, label=r'0.582*(1-\alpha_{Y(bb)})')
plt.plot(alpha, scale_Ybb, label=r'$X\rightarrow Y(bb)H(\tau\tau)$')
plt.plot(alpha, scale_Ytt, label=r'$X\rightarrow Y(\tau\tau)H(bb)$')
plt.plot(alpha, scale_Ytt+scale_Ybb, label='combined')

# Add title and labels
plt.xlabel(r'$\alpha_{Y(bb)}$')
plt.ylabel('scaling value')

# Add a legend
plt.legend()

plt.savefig("alpha_dependence.pdf")
plt.savefig("alpha_dependence.png")
plt.close()