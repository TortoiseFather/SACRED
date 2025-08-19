from statemachine import StateMachine, State
import random
from pygame.locals import *
import pydot
import pygame
import os

class RailwayOperation(StateMachine):
    # Define Variables
    AWSTimer = 0

    # Define states
    idle = State('Idle', initial=True)
    pre_departure_checks = State('Pre_Departure_Checks')
    departure = State('Departure')
    engine_check = State('Engine_Check')
    brake_change = State('Brake_Change')
    speed_change = State('Speed_Change')
    cruise = State('Cruise')
    station_arrival = State('Station_Arrival')
    passenger_boarding = State('Passenger_Boarding')
    passenger_alighting = State('Passenger_Alighting')
    station_departure = State('Station_Departure')
    AWS = State('AWS')
    emergency_stop = State('Emergency_Stop')
    maintenance = State('Maintenance')
    standby = State('Standby')

    approach_mode: bool = False
    next_station_distance: float = 2000.0   # metres (just a simple scalar for now)
    approach_start_distance: float = 1200.0 # start braking when within this distance
    arrival_distance: float = 80.0          # when this close, you’re “at the station”
    approach_target_speed: float = 25.0     # km/h (or pick your unit)
    arrival_speed: float = 8.0              # crawl-in speed



    # Define transitions
    start = idle.to(pre_departure_checks)
    pre_departure = pre_departure_checks.to(departure)
    depart = departure.to(engine_check)
    check_engine = engine_check.to(speed_change, cond='is_engine_forward') | engine_check.to(idle, cond='is_engine_n') | speed_change.to(engine_check)
    brake_check = brake_change.to(speed_change) | brake_change.to(brake_change, cond='brake_not_zero')
    speed_reached = speed_change.to(cruise, cond='is_speed_limit_reached')
    speed_limit_change = cruise.to(brake_change, cond='is_speed_over_limit') | cruise.to(speed_change, cond='is_speed_under_limit') | brake_change.to(speed_change, cond='is_speed_under_limit')
    begin_approach = cruise.to(brake_change, cond='should_stop_next_station')
    approach_arrival = brake_change.to(station_arrival, cond='approach_complete')
    board_passengers = station_arrival.to(passenger_boarding)
    alight_passengers = passenger_boarding.to(passenger_alighting)
    depart_station = passenger_alighting.to(station_departure)
    continue_cruise = station_departure.to(cruise)
    aws_alarm = idle.to(AWS) | engine_check.to(AWS) | brake_change.to(AWS) | speed_change.to(AWS) | cruise.to(AWS) | emergency_stop.to(AWS)
    reset_AWS = AWS.to(engine_check)
    emergency = cruise.to(emergency_stop) | speed_change.to(emergency_stop) | brake_change.to(emergency_stop)
    maintain = emergency_stop.to(maintenance) | station_arrival.to(maintenance)
    standby_state = idle.to(standby)


    def __init__(self):
        self._initialized = False  # Initialization flag
        self.first = 'true'  # Initialization of self.first
        self.engine_check_status = 'n'  # 'f', 'n', 'r', 'x'
        self.brake_level = 8
        self.current_speed = 0
        self.speed_limit = 50
        self.AWSClock = random.randint(10, 11)
        self.idle_status = ''  # Initialize idle_status
        super().__init__()  # Call the parent __init__ method after initialization
        self.update_diagram()
        self._initialized = True  # Set the flag to indicate initialization is complete

    def is_engine_broken(self):
        return self.engine_check_status == 'x'
    def should_stop_next_station(self):
        """We’re in cruise and either the timetable says stop, or the user flags it,
        and we’re within the approach window."""
        return getattr(self, "stopping_here", True) and self.next_station_distance <= self.approach_start_distance

    def approach_complete(self):
        """Close enough and slow enough to nose onto the platform."""
        return self.approach_mode and self.next_station_distance <= self.arrival_distance and self.current_speed <= self.arrival_speed
    
    def _advance_distance(self, dt_sec=1.0):
        # crude kinematics: distance -= speed * dt ; assume current_speed in m/s or convert if needed
        self.next_station_distance = max(0.0, self.next_station_distance - self.current_speed * dt_sec)

    def brake_not_zero(self):
        return self.brake_level != 0

    def is_engine_forward(self):
        return self.engine_check_status == 'f'

    def is_engine_n(self):
        return self.engine_check_status == 'n' and self.brake_level == 8 and self.first == 'false'

    def is_brake_zero(self):
        return self.current_speed >= self.speed_limit and self.brake_level == 0

    def is_speed_limit_reached(self):
        return self.current_speed > self.speed_limit

    def is_speed_over_limit(self):
        return self.current_speed > self.speed_limit

    def is_speed_under_limit(self):
        return self.current_speed < self.speed_limit

    def is_AWS_alarm(self):
        return self.AWSTimer >= self.AWSClock

    def on_enter_idle(self):
        if not self._initialized:
            return  # Do not proceed if still initializing

        if self.first == 'true':  # Directly using self.first
            self.first = 'false'  # Set first to false to avoid reinitialization
            self.pre_departure()
        else:
            if self.idle_status == 'y':
                self.pre_departure()
            elif self.idle_status == 'n':
                self.standby_state()

    def on_enter_engine_check(self):
        print("Entering Engine Check...")
        print("\nCurrent state:", self.engine_check_status)
        self.AWSTimer += 1
        if self.is_AWS_alarm():
            print("AWS alarm triggered. Moving to AWS state...")
            self.aws_alarm()
        else:
            self.engine_check_status = input("Enter engine check status (f/n/r/x): ").strip()
            if self.is_engine_broken():
                print("Engine is broken. Moving to Brake Change...")
                self.check_engine()
            elif self.is_engine_forward():
                print("Engine is forward. Moving to Speed Change...")
                self.check_engine()
            elif self.is_engine_n():
                print("Engine is off. Moving to Idle...")
                self.check_engine()
        self.update_diagram()

    def on_enter_brake_change(self):
        print("\nCurrent state:", self.current_state)
        self.update_diagram()
        print("Changing Brakes...")
        self.AWSTimer += 1
        if self.is_AWS_alarm():
            print("AWS alarm triggered. Moving to AWS state...")
            self.aws_alarm()
            return

        # --- APPROACH LOGIC (adds only a few lines) ---
        if self.approach_mode:
            print(f"[Approach] target≤{self.approach_target_speed} and distance≤{self.arrival_distance}")
        while True:
            # advance distance a little each iteration (very rough ‘tick’)
            self._advance_distance(dt_sec=1.0)

            # choose brake based on whether we’re in approach or just overspeed
            prompt = "Enter brake level (0-8 or negative for emergency): " if not self.approach_mode else \
                     f"[Approach] dist={self.next_station_distance:.0f}m, v={self.current_speed:.1f} — brake (0-8, neg for EMR): "
            self.brake_level = int(input(prompt))

            if self.brake_level < 0:
                print("Emergency brake triggered!")
                self.emergency()
                return

            self.current_speed = max(0, self.current_speed - self.brake_level)  # simple decel model
            print(f"Current speed: {self.current_speed}, Brake level: {self.brake_level}")

            # **Key**: if approach + thresholds met → arrive
            if self.approach_complete():
                print("Approach complete. Entering Station Arrival...")
                self.approach_arrival()   # jump to Station_Arrival
                self.approach_mode = False
                return

            # end loop if no longer need braking (falls back to your existing path)
            if not self.is_speed_limit_reached() and self.brake_level == 0 and not self.approach_mode:
                print("Brake change complete. Moving to Speed Change...")
                self.brake_check()
                return

    def on_enter_emergency_stop(self):
        print("Entering Emergency Stop state.")
        # Add any additional logic you want to handle during the emergency stop

    def on_enter_speed_change(self):
        print("Changing Speed...")
        print("Speed limit = ", self.speed_limit)
        self.update_diagram()
        self.AWSTimer += 1
        self.first = 'false'
        if self.speed_limit == 0:
            print("Speed limit 0, moving to engine shutdown")
            self.brake_level = 8
            self.engine_check_status = 'n'
            self.check_engine()
        else:
            while self.current_speed <= self.speed_limit:
                if self.is_AWS_alarm():
                    print("AWS alarm triggered. Moving to AWS state...")
                    self.aws_alarm()
                    return
                self.engine_speed = int(input("Enter engine speed (0-10): "))
                self.current_speed += self.engine_speed
                print(f"Current speed: {self.current_speed}, Engine speed: {self.engine_speed}")
                if self.is_speed_limit_reached():
                    print("Speed limit reached. Moving to Cruise...")
                    self.speed_reached()
                    return
            else:
                if self.is_speed_limit_reached():
                    print("Speed limit reached. Moving to Cruise...")
                    self.speed_reached()
                else:
                    print("This shouldn't happen.")

    def on_enter_cruise(self):
        print("\nCurrent state:", self.current_state)
        self.update_diagram()
        print("Cruising...")

        # OPTIONAL: ask once whether we’re stopping at next station & distance
        try:
            stop = input("Stopping at next station? (y/n, default y): ").strip().lower()
            self.stopping_here = (stop != 'n')
            if self.stopping_here:
                d = input(f"Distance to next station in metres (current {self.next_station_distance}): ").strip()
                if d:
                    self.next_station_distance = float(d)
        except Exception:
            self.stopping_here = True

        self.AWSTimer += 1
        if self.is_AWS_alarm():
            print("AWS alarm triggered. Moving to AWS state...")
            self.aws_alarm()
            return

        # existing speed limit handling (unchanged)
        self.speed_limit = int(input("Enter new speed limit: "))
        print(f"New speed limit: {self.speed_limit}")

        # if we need to start the approach, hop to Brake_Change with a flag
        if self.should_stop_next_station():
            print("Within approach window. Begin braking for station approach...")
            self.approach_mode = True
            self.begin_approach()
            return

        if self.is_speed_over_limit():
            print("Speed over limit. Moving to Brake Change...")
            self.speed_limit_change()
        elif self.is_speed_under_limit():
            print("Speed under limit. Moving to Speed Change...")
            self.speed_limit_change()
        self.update_diagram()

    def on_enter_AWS(self):
        print("\nCurrent state:", self.current_state)
        self.update_diagram()

        self.AWSTimer = 0
        print("AWS Acknowledged")
        print(self.AWSTimer)
        self.AWSClock = random.randint(10, 40)
        print(self.AWSClock)
        self.reset_AWS()
        self.update_diagram()

    def start_initial_transition(self):
        if self.current_state == self.idle:
            self.start()

    def update_diagram(self):
        dot_content = self._graph().to_string()
        dot_content_cleaned = dot_content.replace('pt', '')

        # Write the cleaned DOT content to a file
        dot_file_path = "TrainSM.dot"
        with open(dot_file_path, "w") as f:
            f.write(dot_content_cleaned)

        # Generate the PNG file using Graphviz
        graphs = pydot.graph_from_dot_file(dot_file_path)
        graphs[0].write_png("TrainSM.png")
        graphs[0].write_pdf("TrainSM.pdf")
def display_diagram():
    pygame.init()
    screen = pygame.display.set_mode((3440, 1000))
    pygame.display.set_caption("State Machine Diagram")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear the screen
        screen.fill((255, 255, 255))

        # Load the latest state machine diagram
        if os.path.exists("TrainSM.png"):
            diagram = pygame.image.load("TrainSM.png")
            screen.blit(diagram, (0, 0))
        pygame.display.flip()
        pygame.time.wait(1000)  # Update every second

    pygame.quit()

# Create instance of RailwayOperation state machine
sm = RailwayOperation()

# Start the initial transition after initialization
sm.start_initial_transition()

print("Starting Railway Operation...")

import threading
display_thread = threading.Thread(target=display_diagram)
display_thread.start()

# Simulate real-time input handling
while True:
    print("\nCurrent state:", sm.current_state)
    sm.AWSTimer += 1
    if sm.is_AWS_alarm():
        sm.aws_alarm()  # Trigger the AWS transition
    else:
        if sm.current_state == sm.idle and sm.first != 'true':  # Directly using sm.first
            sm.AWSTimer -= 1
            sm.idle_status = input("Train at stop, are you ready to continue? (y/n/k): ").strip()
            if sm.idle_status == 'y':
                sm.pre_departure()
            elif sm.idle_status == 'n':
                sm.standby_state()
            elif sm.idle_status == 'k':
                print("Stall: Waiting in idle state.")
            else:
                print("Invalid command. Please enter 'y', 'n', or 'k'.")
        elif sm.current_state == sm.pre_departure_checks:
            sm.pre_departure()
        elif sm.current_state == sm.departure:
            sm.depart()
        elif sm.current_state == sm.engine_check:
            sm.engine_check_status = input("Enter engine check status (f/n/r/x): ").strip()
            if sm.engine_check_status in ['f', 'n', 'r', 'x']:
                sm.on_enter_engine_check()
            else:
                print("Invalid engine check status. Please enter 'f', 'n', 'r', or 'x'.")
        elif sm.current_state == sm.brake_change:
            try:
                sm.brake_level = int(input("Enter brake level (0-8): "))
                if 0 <= sm.brake_level <= 8:
                    sm.on_enter_brake_change()
                else:
                    print("Invalid brake level. Please enter a value between 0 and 8.")
            except ValueError:
                print("Invalid input. Please enter a numerical value between 0 and 8.")
        elif sm.current_state == sm.speed_change:
            sm.on_enter_speed_change()
        elif sm.current_state == sm.cruise:
            sm.on_enter_cruise()
        elif sm.current_state == sm.station_arrival:
            sm.on_enter_station_arrival()
        elif sm.current_state == sm.passenger_boarding:
            sm.on_enter_passenger_boarding()
        elif sm.current_state == sm.passenger_alighting:
            sm.on_enter_passenger_alighting()
        elif sm.current_state == sm.station_departure:
            sm.on_enter_station_departure()
        elif sm.current_state == sm.emergency_stop:
            sm.on_enter_emergency_stop()
        elif sm.current_state == sm.maintenance:
            sm.on_enter_maintenance()
        elif sm.current_state == sm.standby:
            sm.on_enter_standby()
