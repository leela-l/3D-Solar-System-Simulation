# 3D Solar System Simulation

A 3D physics simulation modelling gravitational interactions between multiple objects in space, built with Python and object-oriented design. The simulation numerically integrates position and velocity over time and includes a GUI for configuring parameters and a comparative plotting tool for analysing the results.

<!-- ![Simulation screenshot](screenshot.png) -->

## Features

- **N-body physics engine**: objects are modelled as classes, with each body's position and velocity updated at every timestep based on the gravitational forces acting on it
- **Numerical integration with NumPy**: vector calculations update positions and velocities over time
- **Interactive GUI (PySimpleGUI)**: set simulation parameters (e.g. object masses, starting positions/velocities, timestep, duration) before running, without touching code
- **Visualisation with Matplotlib**: plot trajectories, forces, energy, and distance between objects over the course of a simulation


## 

- Python
- NumPy: numerical integration
- Matplotlib: visualisation and graphing
- PySimpleGUI:  parameter input GUI

## Getting started

### Requirements

- Python 3.11
- `numpy`
- `matplotlib`
- `PySimpleGUI`

### Installation

```bash
git clone https://github.com/leela-l/3D-Solar-System-Simulation.git
cd 3D-Solar-System-Simulation
pip install numpy matplotlib PySimpleGUI
```

### Running the simulation

```bash
python main.py
```

This opens the GUI, where you can set your desired simulation parameters before running.
