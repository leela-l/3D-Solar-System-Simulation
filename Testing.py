# Import necessary modules
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Defines theme
sg.theme('DarkBlue')


class SolarSystem:
    # Class defining system containing planets and grid
    def __init__(self, input_show_orbits, input_show_v_labels, input_show_f_arrows):
        self.background = plt.style.use('dark_background')
        # Define background and grid
        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(projection='3d')
        # Define number of planets in solar system as 0
        self.bodies = []
        # Define constants in solar system
        self.__G = 6.67430e-11
        self.__dt = 24 * 60 * 60  # Timestep for each frame (seconds in a day)
        self.__scale_distance = 1.5e11  # AU distance
        self.t = 0  # Sets time at 0
        # Initialises these lists as empty, so they can be appended to later
        self.planet_dots = []
        self.planet_lines = []
        # Functionality of hide/show orbits, velocity labels is dependent on user input
        self.show_orbits = input_show_orbits
        self.show_v_labels = input_show_v_labels
        self.show_f_arrows = input_show_f_arrows
        # Defines offset distance so label does not cover planet
        self.label_position_offset = (self.__scale_distance / 8)
        # Sets animation as empty
        self.ani = None
        # Variable to keep track if collision has already occurred in simulation
        self.collision_occurred = False
        # Stores a list of the 2 planets that have crashed
        self.crashed_planets = []

    def get__G(self):
        return self.__G

    def get__dt(self):
        return self.__dt

    def get__scale_distance(self):
        return self.__scale_distance

    def set_grid(self):
        # Removes gray background of grid
        self.ax.xaxis.pane.fill = False
        self.ax.yaxis.pane.fill = False
        self.ax.zaxis.pane.fill = False

        # Makes edges black so they cannot be seen
        self.ax.xaxis.pane.set_edgecolor('black')
        self.ax.yaxis.pane.set_edgecolor('black')
        self.ax.zaxis.pane.set_edgecolor('black')

        # Makes grid black so it blends with the background
        self.ax.xaxis._axinfo["grid"]['color'] = (0, 0, 0, 0)
        self.ax.yaxis._axinfo["grid"]['color'] = (0, 0, 0, 0)
        self.ax.zaxis._axinfo["grid"]['color'] = (0, 0, 0, 0)

        # Removes labels from axis
        self.ax.xaxis.set_tick_params(labelbottom=False)
        self.ax.yaxis.set_tick_params(labelleft=False)
        self.ax.zaxis.set_tick_params(labelleft=False)

        # Sets limits for x and y-axis and scales them correctly
        self.ax.set_xlim(-2 * self.get__scale_distance(), 2 * self.get__scale_distance())
        self.ax.set_ylim(-2 * self.get__scale_distance(), 2 * self.get__scale_distance())
        self.ax.set_zlim(-2 * self.get__scale_distance(), 2 * self.get__scale_distance())

        # Ensures that the aspect ratio should be determined by the size of the bounding box containing the axes
        plt.gca().set_aspect('equal', adjustable='box')

    def set_labels(self):
        # Set labels on the axes
        self.ax.set_xlabel('X')
        self.ax.set_ylabel('Y')
        self.ax.set_zlabel('Z')

        # Title for simulation
        plt.title('3D Solar System Simulation', fontsize=15)

    def add_body(self, body):
        # Adds body object specified to list
        self.bodies.append(body)

    def remove_body(self, body):
        # Removes body object specified from list
        self.bodies.remove(body)

    def display_plot(self):
        # Iterates through all planets in body list
        for i in range(len(self.bodies)):
            # Displays planet
            self.bodies[i].display()
        # Draws plot to canvas
        plt.draw()

    def create_animation(self, planets):
        # Method for defining simulation

        # Sets background of simulation
        self.set_grid()
        self.set_labels()

        # Iterates through all planets
        for i in range(len(planets)):
            # Adds them to solar system
            self.add_body(planets[i])

        # Displays all planets & grid
        self.display_plot()

        # Runs animation
        self.ani = FuncAnimation(self.fig, self.update, frames=1000, interval=1, blit=False)
        return self.ani

    def calc_new_positions(self):
        # Iterates through each planet
        for i in range(len(self.bodies)):

            # Updates position of each 'dot' in graph
            self.bodies[i].dot.set_data([self.bodies[i].position[0]], [self.bodies[i].position[1]])  # X,Y
            self.bodies[i].dot.set_3d_properties(self.bodies[i].position[2])  # Z

            # Adds updated dot to list
            self.planet_dots.append(self.bodies[i].dot)

            # Retrieves data of all positions that planet has covered
            data = self.bodies[i].record_line_data()
            # Stores x,y,z coordinates of each planet to lists
            x, y, z = zip(*data)

            # Checks if user wants to show orbit
            if self.show_orbits == True:
                # Sets line
                self.bodies[i].path.set_data(x, y)  # X,Y
                self.bodies[i].path.set_3d_properties(z)  # Z
                # Stores each line in this list
                self.planet_lines.append(self.bodies[i].path)

            # If user does not want to show orbit, planet_lines set to none so does not return line
            else:
                self.planet_lines = None

    def move_bodies(self):
        # Defines empty list which is as long as number of planets in system
        forces = []
        GPE = []
        for i in range(len(self.bodies)):
            forces.append(0)
            GPE.append(0)

        # Iterates through each planet
        for i in range(len(self.bodies)):
            # Initialises total force for planet i as 0
            force = 0
            # Iterates again though each planet
            for j in range(len(self.bodies)):
                # Checks if both planets are the same to prevent it from calculation force on itself
                if i != j:
                    # Adds force of body i on body j to total force on body i
                    force += -(self.bodies[i].calc_force(self.bodies[j]))
                    # Calculates distance between bodies
                    r = np.linalg.norm(self.bodies[i].position - self.bodies[j].position)
                    # Finds GPE using GMm/r
                    gpe = (self.get__G() * self.bodies[i].mass * self.bodies[j].mass) / r
                # Checks if it has iterated through all the planets
                if j == (len(self.bodies) - 1):
                    # If so, it updates the total force to the forces array & also gpe
                    forces[i] = (force)
                    GPE[i] = gpe

        # Iterates again though each planet
        for i in range(len(self.bodies)):
            # Adds size of force to list
            self.bodies[i].force_vals.append(np.linalg.norm(forces[i]))
            # Adds size of acceleration to list using F = ma
            self.bodies[i].acc_vals.append(np.linalg.norm(forces[i] / self.bodies[i].mass))
            # Adds size of distance to list
            self.bodies[i].dist_vals.append(np.linalg.norm(self.bodies[i].position))
            # Adds size of velocity to list
            self.bodies[i].vel_vals.append(np.linalg.norm(self.bodies[i].velocity))
            # Adds current time to list
            self.bodies[i].time_vals.append(self.t)
            # Calculates kinetic energy using 0.5m*v^2
            ke = 0.5 * self.bodies[i].mass * (np.linalg.norm(self.bodies[i].velocity) ** 2)
            self.bodies[i].KE_vals.append(ke)
            self.bodies[i].GPE_vals.append(-GPE[i])

            # Moves position of body
            self.bodies[i].move(forces[i])

    def update_time(self):
        # Increases time by timestep
        self.t += self.__dt
        # Calculates time in years & displays to 3 decimal places
        days = self.t / 86400
        years = days / 365.25
        time = round(years, 3)
        gui.solar_system.ax.set_title(f'Solar System: t = {time} years')

    def validate_crash(self):
        # initialises crash text as empty
        crash_text = gui.solar_system.ax.text(0, 0, 0, '', color='white', fontsize=6)

        # Iterates through each planet
        for i in range(len(self.bodies)):
            # Iterates through each planet
            for j in range(len(self.bodies)):
                # Checks that it is not calculating crash instance on itself
                if i != j:
                    # Defines boundary positions for collisions on planet i
                    upper_boundary = self.bodies[i].position + np.array([1e10, 1e10, 1e10])
                    lower_boundary = self.bodies[i].position - np.array([1e10, 1e10, 1e10])

                    # Defines condition that must be met for a crash to occur
                    # If coordinates of planet j are within range of collision positions for planet i
                    collision_condition = np.all(
                        (self.bodies[j].position <= upper_boundary) & (self.bodies[j].position >= lower_boundary))

                    # If collision is met and planets haven't crashed before
                    if self.bodies[j].crash != True and collision_condition:
                        if not self.collision_occurred:
                            # Sets crash text at position of collision
                            crash_text.set_x(self.bodies[j].position[0])
                            crash_text.set_y(self.bodies[j].position[1])
                            crash_text.set_3d_properties(z=self.bodies[j].position[2])
                            # Sets text to 'crash'
                            crash_text.set_text('crash')
                            self.bodies[j].crash = True
                            # Collision has occurred
                            self.collision_occurred = True
                            # Add planets to planets crashed list
                            self.crashed_planets.append(i + 1)
                            self.crashed_planets.append(j + 1)
                            # Stops animation
                            self.ani.event_source.stop()

    def display_vel_label(self):
        # Iterates through each planet
        for i in range(len(self.bodies)):
            # Rounds the velocity value to 3d.p.
            velocity = int(round(np.linalg.norm(self.bodies[i].velocity), 3))
            # Displays velocity label at position of planet i + an offset, so it does not cover the planet
            self.bodies[i].v_label.set_x(self.bodies[i].position[0] + self.label_position_offset)
            self.bodies[i].v_label.set_y(self.bodies[i].position[1] + self.label_position_offset)
            self.bodies[i].v_label.set_3d_properties(z=self.bodies[i].position[2])
            # Text shows the velocity
            self.bodies[i].v_label.set_text(f'v = {velocity} ms⁻¹')

    def display_f_arrows(self):
        # Iterates through each planet
        for i in range(len(self.bodies)):
            # Removes existing arrow on graph
            self.bodies[i].f_arrow.remove()
            # Adds new arrow at current position of planet i
            self.bodies[i].f_arrow = self.ax.quiver(self.bodies[i].position[0], self.bodies[i].position[1],
                                                    self.bodies[i].position[2], self.bodies[i].velocity[0],
                                                    self.bodies[i].velocity[1],
                                                    self.bodies[i].velocity[2], color='white',
                                                    # Calculate length that is proportional in size to force (ratio of force)
                                                    # So it appears on screen in visable size
                                                    length=(np.linalg.norm(self.bodies[i].velocity) / 5197) * (
                                                        self.get__scale_distance()),
                                                    # Define aesthetic of arrow
                                                    normalize=True, linewidth=0.5, arrow_length_ratio=0.3)

    def update(self, frame):

        self.move_bodies()

        self.calc_new_positions()

        self.validate_crash()

        self.update_time()

        # Checks if user has specified that labels should be present
        if self.show_v_labels:
            self.display_vel_label()

        # Checks if user has specified that arrows should be present
        if self.show_f_arrows:
            self.display_f_arrows()

        # Returns list of dot representations and lines of each planet
        return self.planet_dots, self.planet_lines


class Body():
    # Class for creating body in solar system
    def __init__(self, input_mass, input_position, input_colour, input_velocity, input_name):
        # Defining attributes of planet that user can change
        self.mass = input_mass
        self.position = input_position  # [x,y,z]
        self.colour = input_colour
        self.velocity = input_velocity  # [xv,yv,zv]
        self.name = input_name
        self.dot = None  # Display of planet on screen
        self.line_data = []  # Data used to display the line path of each planet
        self.path = None  # Line showing trail of planet
        self.v_label = gui.solar_system.ax.text(0, 0, 0, '', color='white', fontsize=6)  # Velocity label
        self.f_arrow = gui.solar_system.ax.quiver(0, 0, 0, 0, 0, 0)  # Force arrow
        self.crash = False  # Checks if crash has occurred on that particular planet
        # Empty lists for storage of every frame's values to be graphed
        self.time_vals = []
        self.force_vals = []
        self.acc_vals = []
        self.dist_vals = []
        self.vel_vals = []
        self.KE_vals = []
        self.GPE_vals = []

    def display(self):
        # Displays body on grid at specified position
        self.dot, = gui.solar_system.ax.plot([self.position[0]], [self.position[1]], [self.position[2]],
                                             'o', color=self.colour, markersize=3)
        # Displays path line of planet
        self.path, = gui.solar_system.ax.plot([], [], self.colour, label=self.name)

    def calc_force(self, o_body):
        # Calculates vector between centre of 2 bodies
        r = np.array(o_body.position) - np.array(self.position)
        # Magnitude of r
        d = np.linalg.norm(r)
        # Calculates force using newtons law of gravitation
        force = np.array((gui.solar_system.get__G() * self.mass * o_body.mass) / (d ** 2))
        # Force multiplied by unit vector to give direction
        force_vector = force * (r / d)
        # Returns force, so it can be passed into move() later in code
        # Negative of force because it is attractive
        return -force_vector

    def move(self, force):
        # Calculates acceleration due to Newton's 2nd law of motion (F=ma)
        a = force / self.mass
        # Updates velocity of body using euler integration, by multiplying acceleration by a timestep
        self.velocity += a * gui.solar_system.get__dt()
        # Updates position of body
        self.position += self.velocity * gui.solar_system.get__dt()

    def record_line_data(self):
        # Adds the current position of the planet to a list of line data
        self.line_data.append(self.position.copy())
        # Returns the current line data list
        return self.line_data


class Graph():
    def __init__(self, input_variable_1, input_variable_2, variables_vals):
        # Sets variables according to input by user
        self.variable_1 = input_variable_1
        self.variable_2 = input_variable_2
        # Collects list of variables stored to be used on thr graph
        self.variable_vals = variables_vals
        # Defines the plot
        self.fig, self.ax = plt.subplots(figsize=(9, 5))

    def graph_simulation(self, solar_system):
        # Clears existing plot
        self.ax.clear()
        # Iterates through each coordinate set
        for i in range(len(self.variable_vals)):
            # Stores y coordinate
            y_values = self.variable_vals[i][0]
            # stores x coordinates list
            x_values = self.variable_vals[i][1]

            # adds plot point to graph on th colour of that planet
            self.ax.plot(x_values, y_values, label=f'Planet {i + 1}', color=solar_system.bodies[i].colour)

        # Sets axis label for graph
        self.ax.set_ylabel(f'{self.variable_1}')
        self.ax.set_xlabel(f'{self.variable_2}')
        # Title of graph
        self.ax.set_title('Comparison of Selected Variables')
        # Creates legend
        self.ax.legend()
        # Draws to canvas
        plt.draw()

class GUI():
    # Class defining user interface
    def __init__(self):
        # Define layout in first column
        self.column1 = [
            # Define title
            [sg.Text('Space system', font=('Helvetica', 35), text_color='#CF9FFF')],
            # Explain inputs
            [sg.Text('Enter starting coordinates between -20 and 20 for each of the planets.',
                     font=('Helvetica', 15))],
            [sg.Text('Enter initial velocity between 0 and 3000 for each of the planets.',
                     font=('Helvetica', 15))],
            # Creates input rows
            [sg.Column([self.create_row(1)])],
            [sg.Column([self.create_row(2)])],
            [sg.Column([self.create_row(3)])],
            [sg.Column([self.create_row(4)])],
            # Buttons to add/remove planets' input fields
            [sg.Button('Add Body', enable_events=True, key='-ADD_BODY-', font=('Helvetica', 15)),
             sg.Button('Remove Body', enable_events=True, key='-REMOVE_BODY-', font=('Helvetica', 15))]
        ]

        # Define second column with buttons and simulation
        self.column2 = [
                        [sg.Button('Start Simulation', enable_events=True, key='-START-', font=('Helvetica', 15)),
                         sg.Button('Stop Simulation', enable_events=True, key='-STOP-', font=('Helvetica', 15)),
                         sg.Button('Reset Simulation', enable_events=False, key='-RESET-', font=('Helvetica', 15)),
                         sg.Button('Exit', enable_events=True, key='-EXIT-', font=('Helvetica', 15))],
                        # Canvas for the simulation to go on
                        [sg.Canvas(key='-CANVAS-', size=(800, 600))],
                        [sg.Button('Help', enable_events=True, key='-HELP-', font=('Helvetica', 15)),
                         sg.Button('Learn', enable_events=True, key='-LEARN-',
                                   tooltip='Get information about simulation', font=('Helvetica', 15)),
                         sg.Button('Graph', enable_events=True, key='-VARS-', tooltip='Graphing tool',
                                   font=('Helvetica', 15))]
        ]

        # Defines layout of GUI
        self.layout = [[
            sg.Column(self.column1),
            # Separator line for aesthetic
            sg.VSeperator(),
            sg.Column(self.column2),
        ]]

        # Defines window for GUI
        self.window = sg.Window('Space Simulation', self.layout, use_default_focus=False, finalize=True)
        # Makes solar system class an attribute of the GUI
        self.solar_system = SolarSystem(True, True, True)
        # Sets planets in solar system as empty
        self.planets = []
        # Sets the canvas for the simulation as empty
        self.figure_canvas_simulation = None
        # Variable used to check if animation is running - initially false as no animation
        self.animation_running = False
        # Variable used to check if values are already stored in the simulation
        self.values_stored = False
        # List of colours for each planet
        self.colours = ['blue', 'green', 'purple', 'pink']
        # Graph non-existent at beginning
        self.graph = None

    def create_row(self, row_number):
        row = [sg.pin(
            sg.Col([
                # Blank for spacing
                [sg.Text(' ', font=('Helvetica', 10))],
                # Title for inputs for that planet
                [sg.Text(f'Planet {row_number}', key=('-STATUS-', row_number - 1), font=('Helvetica', 15),
                         text_color='#CF9FFF')],
                [  # Input mass slider
                    sg.Text(f'Mass:', font=('Helvetica', 15)),
                    sg.Slider(range=(24, 32), orientation='h', resolution=1,
                              key=f'-MASS{row_number}-',
                              size=(15, 15), font=('Helvetica', 15), default_value=28)
                ],
                [  # Input coordinates x,y,z
                    sg.Text(f'Starting coordinates:', font=('Helvetica', 15)),
                    sg.Text('X', font=('Helvetica', 15)),
                    sg.Input(key=f'-X{row_number}-', do_not_clear=True, size=(3, 1), font=('Helvetica', 15),
                             default_text=str(row_number * 5)),
                    sg.Text('Y', font=('Helvetica', 15)),
                    sg.Input(key=f'-Y{row_number}-', do_not_clear=True, size=(3, 1), font=('Helvetica', 15),
                             default_text='0'),
                    sg.Text('Z', font=('Helvetica', 15)),
                    sg.Input(key=f'-Z{row_number}-', do_not_clear=True, size=(3, 1), font=('Helvetica', 15),
                             default_text='0'),
                ],
                [  # Input velocity x,y,z
                    sg.Text(f'Initial velocity:', font=('Helvetica', 15)),
                    sg.Text('X', font=('Helvetica', 15)), sg.Input(key=f'-XV{row_number}-', do_not_clear=True,
                                                                   size=(5, 1), font=('Helvetica', 15),
                                                                   default_text=str(row_number * 100)),
                    sg.Text('Y', font=('Helvetica', 15)), sg.Input(key=f'-YV{row_number}-', do_not_clear=True,
                                                                   size=(5, 1), font=('Helvetica', 15), default_text=0),
                    sg.Text('Z', font=('Helvetica', 15)),
                    sg.Input(key=f'-ZV{row_number}-', do_not_clear=True, size=(5, 1), font=('Helvetica', 15),
                             default_text=row_number * 400)
                ]],
                key=('-ROW-', row_number)
            ))]
        return row

    def draw_figure_simulation(self, canvas, figure):
        # Draws simulation to canvas
        self.figure_canvas_simulation = FigureCanvasTkAgg(figure, canvas)
        self.figure_canvas_simulation.draw()
        self.figure_canvas_simulation.get_tk_widget().pack(side='top', fill='both', expand=1)
        # Returns drawing
        return self.figure_canvas_simulation

    def draw_figure_graph(self, canvas, figure):
        # Draws graph to canvas
        self.figure_canvas_graph = FigureCanvasTkAgg(figure, canvas)
        self.figure_canvas_graph.draw()
        self.figure_canvas_graph.get_tk_widget().pack(side='top', fill='both', expand=1)
        # Returns drawing
        return self.figure_canvas_graph

    def start_simulation(self, row_counter, values):
        # Checks if the animation is not already running
        if not self.animation_running:

            # Iterates through each row of values
            for i in range(row_counter):
                # Checks if no inputs are entered
                if (values[f'-X{i + 1}-'] == '') and (values[f'-Y{i + 1}-'] == '') and (values[f'-Z{i + 1}-'] == '') \
                        and (values[f'-XV{i + 1}-'] == '') and (values[f'-YV{i + 1}-'] == '') and (
                        values[f'-ZV{i + 1}-'] == ''):
                    # If so produces pop up so that user knows which input was wrong and why
                    sg.popup_error(f'Please fill in all input fields', font=('Helvetica', 15))
                    # Exits function so that code does not run
                    return

                # Checks if inputs are an empty string
                if (values[f'-X{i + 1}-'] == '') or (values[f'-Y{i + 1}-'] == '') or (values[f'-Z{i + 1}-'] == '') or \
                        (values[f'-XV{i + 1}-'] == '') or (values[f'-YV{i + 1}-'] == '') or (
                        values[f'-ZV{i + 1}-'] == ''):
                    # If so produces pop up so that user knows which input was wrong and why
                    sg.popup_error(f'Please fill in all inputs for Planet {i + 1}', font=('Helvetica', 15))
                    # Exits function so that code does not run
                    return

                # Checks if values entered can be converted to float
                try:
                    float(values[f'-X{i + 1}-'])
                    float(values[f'-Y{i + 1}-'])
                    float(values[f'-Z{i + 1}-'])
                    float(values[f'-XV{i + 1}-'])
                    float(values[f'-YV{i + 1}-'])
                    float(values[f'-ZV{i + 1}-'])
                except ValueError:
                    # If error occurs produces pop up so that user knows which input was wrong and why
                    sg.popup_error(f'You must enter integer inputs for Planet {i + 1}', font=('Helvetica', 15))
                    # Exits function so that code does not run
                    return

                unique_coordinates = []

                for i in range(row_counter):
                    coordinates = (values[f'-X{i + 1}-'], values[f'-Y{i + 1}-'], values[f'-Z{i + 1}-'])
                    if coordinates in unique_coordinates:
                        sg.popup_error(f'Error: Planets cannot have the same coordinates.', font=('Helvetica', 15))
                        return  # Stop simulation if duplicate coordinates are found
                    unique_coordinates.append(coordinates)

                # Checks if coordinates are within -20 to 20
                if (float(values[f'-X{i + 1}-']) < -20) or (float(values[f'-Y{i + 1}-']) < -20) or (
                        float(values[f'-Z{i + 1}-']) < -20) or (float(values[f'-X{i + 1}-']) > 20) or (
                        float(values[f'-Y{i + 1}-']) > 20) or (float(values[f'-Z{i + 1}-']) > 20):
                    # If so produces pop up so that user knows which input was wrong and why
                    sg.popup_error(f'Please enter coordinates in the valid range (-20 to 20) for Planet {i + 1}',
                                   font=('Helvetica', 15))
                    # Exits function so that code does not run
                    return

                # Checks if velocities are not all 0
                if (float(values[f'-XV{i + 1}-']) == 0) and (float(values[f'-YV{i + 1}-']) == 0) and (
                        float(values[f'-ZV{i + 1}-']) == 0):
                    # If so produces pop up so that user knows which input was wrong and why
                    sg.popup_error(f'You must enter one non-zero velocity for Planet {i + 1}', font=('Helvetica', 15))
                    # Exits function so that code does not run
                    return

                # Checks if velocities are in range -10000 to 10000
                if (float(values[f'-XV{i + 1}-']) < -10000) or (float(values[f'-YV{i + 1}-']) < -10000) or (
                        float(values[f'-ZV{i + 1}-']) < -10000) or \
                        (float(values[f'-XV{i + 1}-']) > 10000) or (float(values[f'-YV{i + 1}-']) > 10000) or (
                        float(values[f'-ZV{i + 1}-']) > 10000):
                    # If so produces pop up so that user knows which input was wrong and why
                    sg.popup_error(f'Please enter velocities in the valid range (-10000 to 10000) for Planet {i + 1}',
                                   font=('Helvetica', 15))
                    # Exits function so that code does not run
                    return

            # Checks if values are already stored in simulation, so it doesn't override it with new & incorrect ones
            if not self.values_stored:
                # Get masses and coordinates from user input in future
                # Deletes current canvas (simulation)
                self.window['-CANVAS-'].TKCanvas.delete('all')
                # Resets solar system
                self.store_values(row_counter, values)
                # Makes canvas visible to users
                self.window['-CANVAS-'].update(visible=True)

                # Add the plot to the window
                self.draw_figure_simulation(self.window['-CANVAS-'].TKCanvas, self.solar_system.fig)

                # Reset button now disabled as it has already been reset
                self.window['-RESET-'].update(disabled=True)

                # Values are now stored in simulation, so it is set to true
                self.values_stored = True

            else:
                # If values are already stored, animation is resumed
                self.solar_system.ani.resume()

        # True as animation is now running
        self.animation_running = True
        # Disables reset button as simulation is running
        self.window['-RESET-'].update(disabled=True)
        # Disables start button as can't start simulation if it is already running
        self.window['-START-'].update(disabled=True)
        # Enables stop button
        self.window['-STOP-'].update(disabled=False)
        # Disables graph button as program is running
        self.window['-VARS-'].update(disabled=True)

    def store_values(self, row_counter, values):
        for i in range(row_counter):
            # Make inputted value the power of ten
            mass = 1 * (10 ** float(values[f'-MASS{i + 1}-']))
            # Divide coordinates by 10 and scale them to graph
            coords = np.array([((float(values[f'-X{i + 1}-'])) / 10) * self.solar_system.get__scale_distance(),
                               ((float(values[f'-Y{i + 1}-'])) / 10) * self.solar_system.get__scale_distance(),
                               ((float(values[f'-Z{i + 1}-'])) / 10) * self.solar_system.get__scale_distance()])
            # Velocities are inputted as desired
            velocity = np.array([float(values[f'-XV{i + 1}-']),
                                 float(values[f'-YV{i + 1}-']),
                                 float(values[f'-ZV{i + 1}-'])])

            # Creates instance of particular planet
            planet = Body(mass, coords, self.colours[i], velocity, f'Planet {i + 1}')

            # Adds planet to list of all planets
            self.planets.append(planet)

        # Creates animation using inputted planets
        self.solar_system.create_animation(self.planets)

    def stop_simulation(self):
        # Checks if animation exists
        if 'ani' not in locals():
            # If so, it stops
            if self.solar_system.collision_occurred:
                # Disables start button as collision occurred so must be reset
                self.window['-START-'].update(disabled=True)
                # Disables stop button as collision occurred so must be reset
                self.window['-STOP-'].update(disabled=True)
                # Enables reset button as collision occurred so must be reset
                self.window['-RESET-'].update(disabled=False)
                # Enables graph button as simulation stopped
                self.window['-VARS-'].update(disabled=False)
                # Produces pop up to inform user which planets have crashed
                sg.popup_ok(f'Planet {self.solar_system.crashed_planets[0]} has crashed with planet '
                            f'{self.solar_system.crashed_planets[1]}', font=('Helvetica', 15))
                self.solar_system.collision_occurred = False

            elif self.animation_running:
                # Pauses existing animation
                self.solar_system.ani.pause()
                # Enables start button as it is paused so can be resumed
                self.window['-START-'].update(disabled=False)
                # Disables stop button as animation now paused
                self.window['-STOP-'].update(disabled=True)
                # Enables reset button as animation can be reset if user wants to
                self.window['-RESET-'].update(disabled=False)
                # Enables graph button as simulation stopped
                self.window['-VARS-'].update(disabled=False)
                # Animation is now not running so set to false
                self.animation_running = False

    def reset(self):

        # Resets simulation
        self.values_stored = False
        self.solar_system.collision_occurred = False

        # Canvas (simulation) is removed
        self.window['-CANVAS-'].update(visible=False)
        # Simulation can be restarted
        self.window['-START-'].update(disabled=False)
        # Simulation cant stop as not started, so button disabled
        self.window['-STOP-'].update(disabled=True)
        # Disables graph button as no variables to store because simulation reset
        self.window['-VARS-'].update(disabled=True)
        # Planets in system reset
        self.planets = []

        # Checks if canvas exists
        if hasattr(self, 'figure_canvas_simulation'):
            # Destroys canvas
            self.figure_canvas_simulation.get_tk_widget().destroy()
            # Deletes from window
            del self.figure_canvas_simulation

        # Resets instance of solar system class
        self.solar_system = SolarSystem(True, True, True)

    def record_selected_vars(self, var_1, var_2):
        # List of variable names user selected
        variables = [var_1, var_2]
        # Defines empty list storing the values each fame of these variables
        variables_vals = []

        for i in range(len(self.solar_system.bodies)):
            # Defines empty list that will store x and y coordinate for that frame of body i
            x_y = []
            # Iterates through the variables the user selected
            for variable in variables:
                # Checks which variable was selected and adds that value to the list
                if variable == 'Time (s)':
                    x_y.append(self.solar_system.bodies[i].time_vals)
                elif variable == 'Force (N)':
                    x_y.append(self.solar_system.bodies[i].force_vals)
                elif variable == 'Acceleration (ms⁻²)':
                    x_y.append(self.solar_system.bodies[i].acc_vals)
                elif variable == 'Distance (m)':
                    x_y.append(self.solar_system.bodies[i].dist_vals)
                elif variable == 'Velocity (ms⁻¹)':
                    x_y.append(self.solar_system.bodies[i].vel_vals)
                elif variable == 'Kinetic Energy (J)':
                    x_y.append(self.solar_system.bodies[i].KE_vals)
                elif variable == 'Gravitational Potential Energy (J)':
                    x_y.append(self.solar_system.bodies[i].GPE_vals)


            # adds x,y coordinates to list of variables
            variables_vals.append(x_y)
        # Creates graph
        self.graph = Graph(var_1, var_2, variables_vals)
        # Graphs the plot
        self.graph.graph_simulation(self.solar_system)

    def create_help_layout(self):
        # Function creates a new layout each time it is called, so the format reuse rule is not broken
        help_layout = [
            [sg.Text('How do I enter the data?', font=('Helvetica', 20),
                     justification='center', text_color='#CF9FFF')],
            [sg.Text('• Use the slide to select the mass of the planet.',
                     font=('Helvetica', 15))],
            [sg.Text(
                '       • The slider enables you to select a value between 10²⁴ and 10³² kg '
                '(typically astronomical masses)',
                font=('Helvetica', 15))],
            [sg.Text('• Enter starting coordinates between -20 and 20 for each of the planets.',
                     font=('Helvetica', 15))],
            [sg.Text('• Enter initial velocity between -10000 and 10000 for each of the planets.',
                     font=('Helvetica', 15))],
            [sg.Button('Close', key='-CLOSE_HELP-', font=('Helvetica', 15))]
        ]
        return help_layout

    def create_intro_layout(self):
        # Function creates a new layout each time it is called, so the format reuse rule is not broken
        intro_layout = [
            [sg.Text('Welcome to Solar System Simulator', font=('Helvetica', 20),
                     justification='center', text_color='#CF9FFF')],
            [sg.Text('Learn about interactions between masses by testing initial conditions for them,'
                     ' and comparing variables using the graphing tool', font=('Helvetica', 15))],
            [sg.Text('• Use the slide to select the mass of the planet.', font=('Helvetica', 15))],
            [sg.Text(
                '       • The slider enables you to select a value between 10²⁴ and 10³² kg (typically '
                'astronomical masses)',
                font=('Helvetica', 15))],
            [sg.Text('• Enter starting coordinates between -20 and 20 for each of the planets.',
                     font=('Helvetica', 15))],
            [sg.Text('• Enter initial velocity between 0 and 3000 for each of the planets.',
                     font=('Helvetica', 15))],
            [sg.Button('Close', key='-CLOSE_INTRO-', font=('Helvetica', 15))]
        ]
        return intro_layout

    def create_learn_layout(self):
        # Function creates a new layout each time it is called, so the format reuse rule is not broken

        # Page 1 layout
        p1_learn_column = [
            [sg.Text('How does the simulation work', font=('Helvetica', 20), justification='center',
                     text_color='#CF9FFF')],
            [sg.Text("This simulation works by using Newton's law of gravitation",
                     font=('Helvetica', 15))],
            [sg.Image(filename='newton-law-gravitation.png')],
            [sg.Text('The law states:', font=('Helvetica', 15))],
            [sg.Text('     • Every particle attracts every other particle in the universe',
                     font=('Helvetica', 15))],
            [sg.Text('     • The force between them is proportional to the product of their masses',
                     font=('Helvetica', 15))],
            [sg.Text(
                '     • The force is also inversely proportional to the square of the distance between their centres',
                font=('Helvetica', 15))],
            [sg.Button('Next Page', key='-TO_P2-', tooltip='Turns to page 2', font=('Helvetica', 15)),
             sg.Button('Close', key='-LEARN_CLOSE_P1-', tooltip='Close', font=('Helvetica', 15))]
        ]

        # Page 2 Layout
        p2_learn_column = [
            [sg.Text('How does the simulation work', font=('Helvetica', 20), justification='center',
                     text_color='#CF9FFF')],
            [sg.Text("• The simulation calculates the total force felt by each planet, "
                     "which is the vector sum of the other\n force from each other planet in the simulation.",
                     font=('Helvetica', 15))],
            [sg.Text('')],
            [sg.Text('• Use the graphing tool to compare variables. What is the relationship between them?',
                     font=('Helvetica', 15))],
            [sg.Text('')],
            [sg.Text("• If fewer lines display on the graph than the number of planets in your simulation, "
                     "it is because\n two or more planets have the same graph.", font=('Helvetica', 15))],
            [sg.Text('')],
            [sg.Button('What happens when I change initial conditions?', key='-LEARN_RELATIONS-',
                       font=('Helvetica', 15))],
            [sg.Text('')],
            [sg.Button('Back', key='-BACK_TO_1-', tooltip='Turns back to page 1', font=('Helvetica', 15)),
             sg.Button('Next Page', key='-TO_P3-', tooltip='Turns to page 3', font=('Helvetica', 15)),
             sg.Button('Close', key='-LEARN_CLOSE_P2-', tooltip='Close', font=('Helvetica', 15))]
        ]

        # Page 3 layout
        p3_learn_column = [
            [sg.Text('N-Body Problem', font=('Helvetica', 20), justification='center',
                     text_color='#CF9FFF')],
            [sg.Text('• You may notice that planets often crash with one another quickly.',
                     font=('Helvetica', 15))],
            [sg.Text('• The problem of finding a stable orbit is known as the n-body problem.',
                     font=('Helvetica', 15))],
            [sg.Text('• In fact, the only stable  known stable orbit for any N > 2 and three equal masses,'
                     'which is the three body figure-8 orbit as shown below',
                     font=('Helvetica', 15))],
            [sg.Image(filename='3-body-solution.png')],
            [sg.Text('• See if you can find a stable orbit for 2 bodies.',
                     font=('Helvetica', 15))],
            [sg.Button('Back', key='-BACK_TO_2-', tooltip='Turns back to page 2', font=('Helvetica', 15)),
             sg.Button('Close', key='-LEARN_CLOSE_P3-', tooltip='Close',font=('Helvetica', 15))]
        ]

        # Page 2 layout when button pressed
        p2_button_press = [
            [sg.Text('How does the simulation work', font=('Helvetica', 20), justification='center',
                     text_color='#CF9FFF')],
            [sg.Text("• The simulation calculates the total force felt by each planet, "
                     "which is the vector sum of the other\n force from each other planet in the simulation.",
                     font=('Helvetica', 15))],
            [sg.Text('')],
            [sg.Text('• Use the graphing tool to compare variables. What is the relationship between them?',
                     font=('Helvetica', 15))],
            [sg.Text('')],
            [sg.Text("• If fewer lines display on the graph than the number of planets in your simulation, "
                     "it is because two\n or more planets have the same graph.", font=('Helvetica', 15))],
            [sg.Text('')],
            [sg.Button('What happens when I change initial conditions?', key='-LEARN_RELATIONS_PB2-')],
            [sg.Text("• Because F is proportional to mass", font=('Helvetica', 15))],
            [sg.Text('      •  Increasing the mass of one planet, the force felt by this planet and the force it '
                     'applies to\n other planets, will increase', font=('Helvetica', 15))],
            [sg.Text("• Because F is proportional to r²", font=('Helvetica', 15))],
            [sg.Text("      • Changing the initial positions to be closer to one another the force will be greater",
                     font=('Helvetica', 15))],
            [sg.Text("• Because F is proportional to acceleration", font=('Helvetica', 15))],
            [sg.Text("      • Increasing the force of a planet  will increase acceleration", font=('Helvetica', 15))],
            [sg.Text('')],
            [sg.Button('Back', key='-BACK_TO_1_P2B-', tooltip='Turns back to page 1', font=('Helvetica', 15)),
             sg.Button('Next Page', key='-TO_P3_P2B-', tooltip='Turns to page 3', font=('Helvetica', 15)),
             sg.Button('Close', key='-LEARN_CLOSE_P2B-', tooltip='Close', font=('Helvetica', 15))]
        ]

        # Layout of learn window
        learn_layout = [
            [sg.pin(sg.Column(p1_learn_column, key='-P1-'))],
            [sg.pin(sg.Column(p2_learn_column, key='-P2-', visible=False))],
            [sg.pin(sg.Column(p3_learn_column, key='-P3-', visible=False))],
            [sg.pin(sg.Column(p2_button_press, key='-P2B-', visible=False))]
        ]
        return learn_layout

    def create_graph_choosing_layout(self):
        # Defines list of variables user can compare
        variables = ['Force (N)','Kinetic Energy (J)','Gravitational Potential Energy (J)', 'Acceleration (ms⁻²)',
                     'Velocity (ms⁻¹)', 'Distance (m)', 'Time (s)']
        #Creates layout of window with sliders
        graph_choosing_layout = [[sg.Text('Select variables to compare', font=('Helvetica', 20), justification='center',
                                          text_color='#CF9FFF')],
                                 [sg.Combo(variables, font=('Helvetica', 15), expand_x=True, enable_events=True,
                                           key='-LIST1-', readonly=True), sg.Text('VS', font=('Helvetica', 15)),
                                  sg.Combo(variables, font=('Helvetica', 15), expand_x=True, enable_events=True,
                                           key='-LIST2-', readonly=True)], [sg.Button('Graph it', key='-GRAPH-',
                                                                       font=('Helvetica', 15))]]
        return graph_choosing_layout

    def learn_window(self):
        # Used to indicate which page of learn window the user is on
        # Creates learn layout for the window
        learn_layout = self.create_learn_layout()
        # Creates new learn window
        learn_window = sg.Window('Learn', learn_layout, size=(900, 700))

        while True:
            # Waits for user input for 10 milliseconds before returning
            # Values contains values from user input relating to event
            learn_event, learn_values = learn_window.read()

            # If X button clicked or close clicked on any page, close window
            if (learn_event == sg.WIN_CLOSED) or \
                    (learn_event == '-LEARN_CLOSE_P1-') or \
                    (learn_event == '-LEARN_CLOSE_P2-') or \
                    (learn_event == '-LEARN_CLOSE_P3-') or \
                    (learn_event == '-LEARN_CLOSE_P2B-'):
                break

            # If next clicked on page 1, take to page 2
            if learn_event == '-TO_P2-':
                # Hides previous page and displays new one
                learn_window['-P1-'].update(visible=False)
                learn_window['-P2-'].update(visible=True)

            # If next clicked on page 2, take to page 3
            if learn_event == '-TO_P3-':
                # Hides previous page and displays next one
                learn_window['-P2-'].update(visible=False)
                learn_window['-P3-'].update(visible=True)

            # If button clicked on page 2, take to page 2B which shows what the button was hiding
            if learn_event == '-TO_P3_P2B-':
                # Hides previous page and displays next one
                learn_window['-P2B-'].update(visible=False)
                learn_window['-P3-'].update(visible=True)

            # If back clicked on page 2, take to page 1
            if learn_event == '-BACK_TO_1-':
                # Hides current page and displays last one
                learn_window['-P2-'].update(visible=False)
                learn_window['-P1-'].update(visible=True)

            # Takes back to page 1 from page 2 with the button pressed
            if learn_event == '-BACK_TO_1_P2B-':
                # Hides current page and displays last one
                learn_window['-P2B-'].update(visible=False)
                learn_window['-P1-'].update(visible=True)

            # Takes back to page 2 from page 3
            if learn_event == '-BACK_TO_2-':
                # Hides current page and displays last one
                learn_window['-P3-'].update(visible=False)
                learn_window['-P2-'].update(visible=True)

            # If button 'What happens when I change initial conditions?' is pressed
            if learn_event == '-LEARN_RELATIONS-':
                # Displays what button was hiding
                learn_window['-P2-'].update(visible=False)
                learn_window['-P2B-'].update(visible=True)

            # If button 'What happens when I change initial conditions?' is pressed again
            if learn_event == '-LEARN_RELATIONS_PB2-':
                # Removes display of what button was hiding
                learn_window['-P2B-'].update(visible=False)
                learn_window['-P2-'].update(visible=True)

        learn_window.close()

    def intro_window(self):
        # Creates intro window
        intro_window = sg.Window('Introduction', self.create_intro_layout())
        while True:
            # Waits for user input for 10 milliseconds before returning
            # Values contains values from user input relating to event
            intro_event, intro_values = intro_window.read()

            # If X button clicked or close clicked, close window
            if intro_event == sg.WIN_CLOSED or intro_event == '-CLOSE_INTRO-':
                break

        intro_window.close()

    def help_window(self):
        # Creates help window
        help_window = sg.Window('Help', self.create_help_layout())

        while True:
            # Waits for user input for 10 milliseconds before returning
            # Values contains values from user input relating to event
            help_event, help_values = help_window.read()

            # If X button clicked or close clicked, close window
            if help_event == sg.WIN_CLOSED or help_event == '-CLOSE_HELP-':
                break

        help_window.close()

    def graphing_window(self):
        # Creates window to choose variables
        graph_choosing_window = sg.Window('Graph', self.create_graph_choosing_layout())

        while True:
            # Waits for user input for 10 milliseconds before returning
            # Values contains values from user input relating to event
            graph_event, graph_values = graph_choosing_window.read()

            # If window exited
            if graph_event == sg.WIN_CLOSED:
                break
            # If graph it clicked
            elif graph_event == '-GRAPH-':
                # Stores variables selected by user
                var_1 = graph_values['-LIST1-']
                var_2 = graph_values['-LIST2-']
                # Records coordinates of variables
                self.record_selected_vars(var_1, var_2)
                # Closes choosing window
                graph_choosing_window.close()
                # Creates layout for graph window which is a new canvas
                graph_layout = [[sg.Canvas(key='-CANVAS_GRAPH-', size=(800, 600))]]
                # Creates window to display graph
                graph_window = sg.Window('Graphing Tool', graph_layout, use_default_focus=False, finalize=True)
                # Draws graph to canvas
                self.draw_figure_graph(graph_window['-CANVAS_GRAPH-'].TKCanvas, self.graph.fig)

        graph_choosing_window.close()

    def run(self):
        # Function for GUI

        # Initially 4 rows/planets' input fields
        row_counter = 4
        # Makes window fit screen of user
        self.window.Maximize()
        # Displays intro window when program first run
        self.intro_window()

        # Loop for GUI
        while True:

            # Waits for user input for 10 milliseconds before returning
            # Values contains values from user input relating to event
            event, values = self.window.read(timeout=10)

            if event == '-START-':
                # If start simulation button clicked, run method
                self.start_simulation(row_counter, values)

            if event == '-STOP-':
                # If stop simulation button clicked, run method
                self.stop_simulation()

            if event == '-EXIT-' or event == sg.WINDOW_CLOSED:
                # If exit clicked or window closed, stop simulation & break to close window
                self.stop_simulation()
                break

            if event == '-RESET-':
                self.reset()

            if event == '-ADD_BODY-':
                # Checks if there are more than 4 rows
                if row_counter < 4:
                    # Adds another row
                    row_counter += 1
                    # Makes new row visible
                    self.window[('-ROW-', row_counter)].update(visible=True)
                    # Ensures remove button is not disabled
                    self.window['-REMOVE_BODY-'].update(disabled=False)
                else:
                    # Disable ability to add more planets
                    self.window['-ADD_BODY-'].update(disabled=True)

            if event == '-REMOVE_BODY-':
                # Checks if there are more than 2 rows
                if row_counter > 2:
                    # Remove the last row
                    self.window[('-ROW-', row_counter)].update(visible=False)
                    # Ensures add button is not disabled
                    self.window['-ADD_BODY-'].update(disabled=False)
                    row_counter -= 1
                else:
                    # Disable ability to remove more planets
                    self.window['-REMOVE_BODY-'].update(disabled=True)

            if event == '-HELP-':
                self.help_window()

            if event == '-LEARN-':
                self.learn_window()

            if event == '-VARS-':
                self.graphing_window()

        # Closes window
        self.window.close()


# Creates instance of GUI class
gui = GUI()

# Runs GUI window
gui.run()
