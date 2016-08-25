# -*- coding: utf-8 -*-
"""
Created on Mon Aug 22 2016
Python 3.x targeted
@author: Chris Currin & Kira Dusterwalt
"""
import sim_time
from compartment import Compartment
import time
from threading import Timer


class Simulator:
    """
    Main simulation controller
    Singleton Pattern
    A note on patterns: http://stackoverflow.com/questions/1318406/why-is-the-borg-pattern-better-than-the-singleton-pattern-in-python
    """
    __single = None
    __time = None
    __gui = None
    __object_list = None
    run_done = None

    def __init__(self, _gui=True):
        if not Simulator.__single:
            Simulator.__time = sim_time.Time()
            Simulator.__object_list = []
            if _gui:
                import gui
                Simulator.__gui = gui.GUI()
            Simulator.__single = self
        else:
            raise RuntimeError('A Simulator already exists')

    @classmethod
    def get_instance(cls):
        if not cls.__single:
            cls.__single = Simulator()
        return cls.__single

    @classmethod
    def time(cls):
        return cls.__time

    @classmethod
    def gui(cls):
        if cls.__gui is None:
            import gui
            Simulator.__gui = gui.GUI()
        return cls.__gui

    @classmethod
    def object_list(cls, add=None):
        if add is not None:
            cls.__object_list.append(add)
        return cls.__object_list

    @classmethod
    def run(cls, stop: float = None, dt: float = None, plot_update_interval: float = 100,
            data_collect_interval: float = 0.1):
        """
        Run a time-based simulation.
        Each time-registered object is moved forward by dt
        :param stop:
        :param dt:
        :param plot_update_interval: frequency to update graphs (in ms)
        :param data_collect_interval: frequency to collect data for plotting (in ms)
        :return:
        """
        if stop is None:
            stop = cls.__time.stop
        if dt is None:
            dt = cls.__time.dt
        if plot_update_interval < data_collect_interval:
            data_collect_interval = plot_update_interval
        print("run from {0} until {1} with time step of {2} ".format(0, stop, dt))
        cls.run_done = False
        for t in range(0, int(round(stop / dt))):
            for compartment in cls.__object_list:
                compartment.step(dt)
            if t % (data_collect_interval / dt) == 0:
                cls.update_graphs()
            if t % (plot_update_interval / dt) == 0:
                cls.plot_graphs()
        cls.run_done = True
        cls.plot_graphs()
        print(time.clock())
        cls.__gui.block()

    @classmethod
    def update_graphs(cls):
        if cls.run_done is False:
            for graph in cls.__gui.graph_list():
                graph.update()

    @classmethod
    def plot_graphs(cls):
        for graph in cls.__gui.graph_list():
            graph.plot_graph()

    @classmethod
    def register_compartment(cls, compartment):
        """
        Add compartment to list of compartments to be updated at each time step
        :param compartment:
        :return:
        :raise TypeError if compartment not an instance of Compartment
        """
        if isinstance(compartment, Compartment):
            cls.__object_list.append(compartment)
        else:
            raise TypeError("Compartment instance expected {0} given".format(type(compartment)))

    @classmethod
    def dispose(cls):
        cls.__single = None
        cls.__time = None
        cls.__gui = None
        cls.__object_list = None
