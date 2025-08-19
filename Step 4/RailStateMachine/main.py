from statemachine import StateMachine, State
import random
class RailwayOperation(StateMachine):
    # Define Variables
    AWSTimer = 0
    # Define states
    idle = State('Idle', initial=True)
    engine_check = State('Engine_Check')
    brake_change = State('Brake_Change')
    speed_change = State('Speed_Change')
    cruise = State('Cruise')
    AWS = State('AWS')

    # Define transitions
    start = idle.to(engine_check)
    check_engine = engine_check.to(speed_change, cond='is_engine_forward') | engine_check.to(idle, cond='is_engine_n')
    brake_check = brake_change.to(speed_change, cond='is_brake_zero') | brake_change.to(brake_change, cond='brake_not_zero') | brake_change.to(speed_change, cond='is_speed_under_limit')
    speed_reached = speed_change.to(cruise, cond='is_speed_limit_reached')
    speed_limit_change = cruise.to(brake_change, cond='is_speed_over_limit') | cruise.to(speed_change, cond='is_speed_under_limit') | brake_change.to(speed_change, cond='is_speed_under_limit')
    aws_alarm = idle.to(AWS) | engine_check.to(AWS) | brake_change.to(AWS) | speed_change.to(AWS) | cruise.to(AWS)
    reset_AWS = AWS.to(engine_check)

    def __init__(self):
        super().__init__()
        self.first = 'true'
        self.engine_check_status = 'n'  # 'f', 'n', 'r', 'x'
        self.brake_level = 8
        self.current_speed = 0
        self.speed_limit = 50
        self.AWSClock = random.randint(10, 11)

    def is_engine_broken(self):
        return self.engine_check_status == 'x'

    def brake_not_zero(self):
        return self.brake_level != 0

    def is_engine_forward(self):
        return self.engine_check_status == 'f'

    def is_engine_n(self):
        return self.engine_check_status == 'n' and self.brake_level == 8 and self.first == 'false'

    def is_brake_zero(self):
        return self.current_speed > self.speed_limit and self.brake_level == 0

    def is_speed_limit_reached(self):
        return self.current_speed >= self.speed_limit

    def is_speed_over_limit(self):
        return self.current_speed > self.speed_limit

    def is_speed_under_limit(self):
        return self.current_speed < self.speed_limit

    def is_AWS_alarm(self):
        return self.AWSTimer >= self.AWSClock

    def on_enter_engine_check(self):
        print("Entering Engine Check...")
        self.AWSTimer += 1
        if self.is_AWS_alarm():
            print("AWS alarm triggered. Moving to AWS state...")
            self.aws_alarm()
        elif self.is_engine_broken():
            print("Engine is broken. Moving to Brake Change...")
            self.check_engine()
        elif self.is_engine_forward():
            print("Engine is forward. Moving to Speed Change...")
            self.check_engine()

    def on_enter_brake_change(self):
        print("Changing Brakes...")
        self.AWSTimer += 1
        if self.is_AWS_alarm():
            print("AWS alarm triggered. Moving to AWS state...")
            self.aws_alarm()
            return
        while self.current_speed > self.speed_limit or self.brake_level != 0:
            self.brake_level = int(input("Enter brake level (0-8): "))
            self.current_speed -= self.brake_level
            print(f"Current speed: {self.current_speed}, Brake level: {self.brake_level}")
            if not self.is_speed_limit_reached():
                print("Speed limit reached. Please disable Brake...")
        print("Brake change complete. Moving to Speed Change...")
        self.brake_check()

    def on_enter_speed_change(self):
        print("Changing Speed...")
        self.AWSTimer += 1
        self.first = 'false'
        while self.current_speed < self.speed_limit:
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
        print("Cruising...")
        self.AWSTimer += 1
        if self.is_AWS_alarm():
            print("AWS alarm triggered. Moving to AWS state...")
            self.aws_alarm()
            return
        self.speed_limit = int(input("Enter new speed limit: "))
        print(f"New speed limit: {self.speed_limit}")
        if self.is_speed_over_limit():
            print("Speed over limit. Moving to Brake Change...")
            self.speed_limit_change()
        elif self.is_speed_under_limit():
            print("Speed under limit. Moving to Speed Change...")
            self.speed_limit_change()

    def on_enter_AWS(self):
        self.AWSTimer = 0
        print("AWS Acknowledged")
        print(self.AWSTimer)
        self.AWSClock = random.randint(10, 40)
        print(self.AWSClock)
        self.reset_AWS()

# Create instance of RailwayOperation state machine
sm = RailwayOperation()
dot_content = sm._graph().to_string()

# Remove the 'pt' unit from the DOT content
dot_content_cleaned = dot_content.replace('pt', '')

# Write the cleaned DOT content to a file
dot_file_path = "TrainSM.dot"
with open(dot_file_path, "w") as f:
    f.write(dot_content_cleaned)

# Generate the PNG file using Graphviz
import pydot
graphs = pydot.graph_from_dot_file(dot_file_path)
graphs[0].write_png("img/TrainSM.png")
# Start the state machine

print("Starting Railway Operation...")
sm.start()

# Simulate real-time input handling
while True:
    print("\nCurrent state:", sm.current_state)
    sm.AWSTimer += 1
    if sm.is_AWS_alarm():
        sm.aws_alarm()  # Trigger the AWS transition
    else:
        if sm.current_state == sm.engine_check:
            sm.engine_check_status = input("Enter engine check status (f/n/r/x): ").strip()
            sm.on_enter_engine_check()
        elif sm.current_state == sm.brake_change:
            sm.brake_level = int(input("Enter brake level (0-8): "))
            sm.on_enter_brake_change()
        elif sm.current_state == sm.speed_change:
            sm.on_enter_speed_change()
        elif sm.current_state == sm.cruise:
            sm.on_enter_cruise()