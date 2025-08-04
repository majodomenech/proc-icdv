import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

# Generate sample data: a noisy sine wave
x = np.linspace(0, (2*np.pi)/4, 100)
y = np.sin(x) + 0.1 * np.random.randn(len(x))  # sine wave with noise

# Parameters for Savitzky-Golay filter
polynomial_order = 2
window_length = 5  # must be odd

# Compute the sampling interval
dt = x[1] - x[0]

# Compute the first derivative
dy = savgol_filter(y, window_length, polynomial_order, deriv=1) / dt

# Plot the original data and the first derivative
plt.figure(figsize=(8, 6))

plt.subplot(3, 1, 1)
plt.plot(x, y, 'b.-')
plt.title('Original Data (Noisy Sine Wave)')
plt.xlabel('x')
plt.ylabel('y')

plt.subplot(3, 1, 2)
plt.plot(x, dy, 'r.-')
plt.title('First Derivative (Savitzky-Golay)')
plt.xlabel('x')
plt.ylabel('dy/dx')

plt.subplot(3, 1, 3)
plt.plot(x, dy, 'r.-')
plt.title('First Derivative (Savitzky-Golay)')
plt.xlabel('x')
plt.ylabel('dy/dx')

plt.tight_layout()
plt.show()