""" 
@Author: Robert Brown

This program solves the Schrodinger equation for given inital conditions using the finite difference method.
This uses Euler
∂u/∂t = ∂²u/∂x²
with bcs: u(0) = u(x_max) = 0
"""

import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def c_to_tup(x):
    # given a complex number x, returns a tuple of floats for the real and imag parts of x
    return x.real, x.imag

class Wavefunction:
    def __init__(self, initial, 
                 dx=0.02,
                 dt=0.0001,
                 xrange=(0,1),
                 trange=(0,1),
                 boundaries=(0+0j,0+0j)
                    ):
        # class initilizer
        self.dx2 = dx ** 2
        self.dt = dt
        self.mu = dt/(2*dx**2)
        self.nx = int(round((xrange[1] - xrange[0])/(dx)))  # number of space steps
        self.nt = int(round((trange[1] - trange[0])/(dt)))  # number of time steps
        # self.I = np.empty[self.nt]
        self.real = np.empty([self.nt,self.nx])
        self.imag = np.empty([self.nt,self.nx])
        self.shape = self.real.shape            # shape of wavefunction array
        self.x = np.linspace(xrange[0], xrange[1], self.nx)
        self.t = np.linspace(xrange[0], xrange[1], self.nt)
        init = initial(self.x)                  # generate the initial wavefunction
        self.real[0] = np.real(init)
        self.imag[0] = np.imag(init)
        self.boundaries = boundaries
        self._setbcs(0)

    def _setbcs(self, key):
        # make wavefunction satisfy BCs
        self.real[key,  0], self.imag[key,  0] = c_to_tup(self.boundaries[0])
        self.real[key, -1], self.imag[key, -1] = c_to_tup(self.boundaries[1])

    def deriv(self, psi, order=4, dirichlet=True):
        # returns the second spatial derivative of psi, ∂²ψ/∂x²
        # TODO: implement periodic boundary condition
        df = np.empty_like(psi)
        
        # central difference        
        if order == 2:
            # 2nd order central difference for 2nd derivative
            df[1:-1] = (psi[2:] - 2*psi[1:-1] + psi[0:-2])
        elif order == 4:
            # 4th order central difference for 2nd derivative
            df[2:-2] = (-psi[:-4] + 16*psi[1:-3] - 30 * psi[2:-2] + 16*psi[3:-1] - psi[4:])/12 
            df[1] = psi[0] - 2*psi[1] + psi[2]
            df[-2] = psi[-1] - 2*psi[-2] + psi[-3]
        
        if dirichlet:
            # set dirchlet boundary conditions (endpoints are constant -> deriv = 0)
            df[0] = 0
            df[-1] = 0
        else:
            # try to estimate df at psi[0]. psi[-1]. This is usually quite unstable
            df[0] = -1 * psi[0] + 4 * psi[1] - 5*psi[2] + 2 * psi[3] # first point
            df[-1] = -1 * psi[-1] + 4 * psi[-2] - 5*psi[-3] + 2 * psi[-4] # last point
        
        return df / self.dx2

    def solve(self):
        kreal = np.empty([4,self.nx])
        kimag = np.empty([4,self.nx])

        for i in range(0, self.nt - 1):
            kreal[0] = - 0.5 * self.deriv(self.imag[i])
            kimag[0] =   0.5 * self.deriv(self.real[i])

            kreal[1] = - 0.5 * self.deriv(self.imag[i] + self.dt * kreal[0]/2)
            kimag[1] =   0.5 * self.deriv(self.real[i] + self.dt * kimag[0]/2)

            kreal[2] = - 0.5 * self.deriv(self.imag[i] + self.dt * kreal[1]/2)
            kimag[2] =   0.5 * self.deriv(self.real[i] + self.dt * kimag[1]/2)

            kreal[3] = - 0.5 * self.deriv(self.imag[i] + self.dt * kreal[2])
            kimag[3] =   0.5 * self.deriv(self.real[i] + self.dt * kimag[2])

            self.real[i + 1] = self.real[i] + self.dt * ((1 / 6) * kreal[0] + (1 / 3) * kreal[1] + (1 / 3) * kreal[2] + (1 / 6) * kreal[3])
            self.imag[i + 1] = self.imag[i] + self.dt * ((1 / 6) * kimag[0] + (1 / 3) * kimag[1] + (1 / 3) * kimag[2] + (1 / 6) * kimag[3])
            self._setbcs(i)
            

    def prob(self, i):
        return self.real[i] ** 2 + self.imag[i] ** 2

        
        
def initial(x):
    # return 0.3*np.exp(5j*x*np.pi)
    return 0.5 * np.sin(5*x*np.pi)
    # return np.exp(-(x-0.3)**2/0.1**2)

t_int = 0.000005
foo = Wavefunction(initial, dt=t_int, trange=(0,0.2))
foo.solve()
    
fig, ax = plt.subplots()
time = ax.text(.7, .5, '$t = 0$', fontsize=15)
line1, = ax.plot(foo.x, foo.real[0], linewidth=3, color='b')
line2, = ax.plot(foo.x, foo.imag[0], linewidth=3, color='r')


ax.set_xlabel("Position, $x$")
ax.set_ylabel("Wavefunction,  $\\Psi(x, t)$")
ax.set_ylim([-.7,.7])

def animate(i):
    line1.set_ydata(foo.real[i])  # update the data
    line2.set_ydata(foo.imag[i]) 
    time.set_text("t = {0:.4f}".format(t_int*i))
    return line1, line2, ax
    
ani = animation.FuncAnimation(fig, animate, np.arange(0, foo.nt,10), interval=10, blit=False)
plt.show()