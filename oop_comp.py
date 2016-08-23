# -*- coding: utf-8 -*-
"""
Created on Sun Aug 14 22:24:27 2016
Python 3.x targeted
@author: Kira
"""
import numpy as np
import matplotlib.pyplot as plt

# constants
R = 25.69 * 1e-3
F = 96485.0  # R (RT/F) in Volts, where F is Faraday's constant in C/mol
n = 200  # points to plot
gna = 3e-9
gk = 5e-8
gcl = 5e-8  # gna,gk,gcl: conductances in mS/cm^2 conv to S/dm^2 (10^-3/10^-2) - corrected for neuron
ck = 2
cna = 3  # cna,ck: pump (ATPase) stoichiometries
rad = 5 * 1e-5  # radius in um convert to dm
len = 100 * 1e-5  # length in um converted to dm
nao = 138e-3
clo = 119e-3
ko = 2.8e-3  # nao,clo,ko: extracellular concentrations (mM converted to M)
pkcc = 1.0


class Compartment:
    def __init__(self, rad, length, kcc2, z):
        self.rad = rad  # in um
        self.len = length  # in um
        self.gkcc = kcc2  # choose strength of kcc2 here (=0 if not present)
        self.z = z  # intracellular charge of impermeant anions

    # from beyond this point - much work needed!
    def plm(self, p):
        z = self.z
        # create plotting arrays
        Vm = []
        K = []
        Na = []
        Cl = []
        W = []
        X = []
        time = []

        dt = 1e-3  # zero time, dt time step
        tt = 8000.0  # total time
        if p < 10 ** (-6) / F:
            tt = 30000.0
        ts = tt / n  # plotting timestep
        tit = int(round(tt / dt))  # tt total time, tit - total number of steps
        ton = 0
        toff = 15000  # times when pump turned on & off
        ctr = 1  # counter for plotting points
        t = 0  # real time
        sw = 0  # switch for ATPase action

        w = np.pi * rad ** 2 * len  # initial volume in liters
        w1 = w  # initial volume stored for graphing later
        Ar = 4e6  # area constant (F and H method)
        C = 7e-6  # capacitance (F/dm^2)
        FinvCAr = F / (C * Ar)  # (F/C*area scaling constant)

        na = 140e-3
        k = 2.5e-3
        cl = 78.3931e-3
        x = (cl - k - na) / z  # na,k,cl,x: intracellular starting concentrations
        osi = na + k + cl + x  # intracellular osmolarity
        oso = osi  # extracellular osmo (fixed)
        xo = oso - clo - ko - nao  # extracellular concentration of impermeants (here w/ zo=-1)

        for i in range(2, tit):  # loop over time
            if (toff > t) and (t > ton):
                sw = 1
            else:
                sw = 0
            if t > toff:
                sw = 0  # control switch

            V = FinvCAr * (na + k - cl + z * x)  # voltage

            # update arrays for plotting
            if t >= (ctr - 1) * ts:
                Vm.append(1000 * V)
                K.append(1000 * R * np.log(ko / k))
                Na.append(1000 * R * np.log(nao / na))
                Cl.append(1000 * R * np.log(cl / clo))
                W.append(w / w1)
                X.append(z * 1000 * R * np.log(xo / x))
                time.append(t)
                ctr += 1

            jp = p * (na / nao) ** 3  # cubic pump rate update (dependent on sodium gradient)

            # kcc2
            jkcc2 = sw * (gk * pkcc * (k * clo - k * cl))  # Fraser and Huang
            # jkcc2=sw*gk*pkcc*(K[ctr-2]-Cl[ctr-2])/10000.0 #Doyon

            # ionic flux equations
            dna = -dt * Ar * (gna * (V - R * np.log(nao / na)) + cna * jp)
            dk = -dt * Ar * (gk * (V - R * np.log(ko / k)) - ck * jp + jkcc2 * sw)
            dcl = dt * Ar * (gcl * (V + R * np.log(
                    clo / cl)) - jkcc2 * sw)  # dna,dk,dcl: increase in intracellular ion conc during time step dt
            na += dna
            k += dk
            cl += dcl  # increment concentrations

            # update volume
            osi = na + k + cl + x  # intracellular osmolarity
            w2 = (w * osi) / oso  # update volume

            # correct ionic concentrations by volume change
            na = (na * w) / w2
            k = (k * w) / w2
            cl = (cl * w) / w2
            x = (x * w) / w2
            w = w2

            t += dt

    # plot
    def graph(self, time, K, Na, Cl, X, Vm, W):
        plt.figure()
        plt.subplot(2, 1, 1)
        plt.plot(time, K, '-c', time, Na, '-r', time, Cl, '-g', time, X, '-b', time, Vm, '--')
        plt.legend(['E_K', 'E_Na', 'E_Cl', 'E_X', 'V_m'])
        plt.subplot(2, 1, 2)
        plt.plot(time, W, label='relative volume')
        plt.legend()
        plt.show()
        return