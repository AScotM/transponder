import random
import time
import logging

logging.basicConfig(level=logging.INFO)

class Vehicle:
    """Represents a vehicle with a unique ID, speed, and position."""
    def __init__(self, vehicle_id, speed=0):
        self.vehicle_id = vehicle_id
        self.speed = speed  # km/h
        self.position = 0   # kilometers

    def update_position(self, dt):
        # Update position based on speed (assuming constant speed over dt seconds)
        # Convert speed from km/h to km/s: divide by 3600
        self.position += self.speed / 3600 * dt

class Transponder:
    """Simulates a transponder attached to a vehicle."""
    def __init__(self, vehicle):
        self.vehicle = vehicle

    def transmit(self):
        # Return a dictionary with the current state of the vehicle
        return {
            "vehicle_id": self.vehicle.vehicle_id,
            "speed": self.vehicle.speed,
            "position": round(self.vehicle.position, 3)
        }

class TrafficSystem:
    """Manages a collection of vehicles and collects data systematically."""
    def __init__(self):
        self.vehicles = []
        self.transponders = []
        self.data_log = []

    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)
        self.transponders.append(Transponder(vehicle))

    def update_system(self, dt):
        # Update each vehicle's position
        for vehicle in self.vehicles:
            vehicle.update_position(dt)
        # Collect data from each transponder and log it
        for transponder in self.transponders:
            data = transponder.transmit()
            self.data_log.append(data)
            logging.info(f"Transmitting data: {data}")

    def simulate(self, duration, dt):
        # Run the simulation for a given duration (in seconds) with updates every dt seconds
        steps = int(duration / dt)
        for _ in range(steps):
            self.update_system(dt)
            time.sleep(dt)

def exec_dynamic_code(code, globals_dict=None, locals_dict=None):
    """
    Executes dynamic code safely.
    
    WARNING: Using exec can be dangerous if code is untrusted.
    Ensure that only trusted code is executed.
    """
    logging.info("\nExecuting dynamic analysis code:")
    try:
        exec(code, globals_dict, locals_dict)
    except Exception as e:
        logging.error(f"Error executing dynamic code: {e}")

if __name__ == "__main__":
    # Create the traffic system
    system = TrafficSystem()
    
    # Add several vehicles with random speeds between 20 km/h and 60 km/h
    for i in range(3):
        vehicle = Vehicle(vehicle_id=f"Vehicle-{i+1}", speed=random.randint(20, 60))
        system.add_vehicle(vehicle)
    
    # Simulate traffic for 5 seconds, updating every 1 second
    system.simulate(duration=5, dt=1)
    
    # Define dynamic code to analyze the logged data
    # In this example, we flag vehicles speeding above 40 km/h.
    analysis_code = """
for record in system.data_log:
    if record['speed'] > 40:
        print(f"Alert: {record['vehicle_id']} is speeding at {record['speed']} km/h!")
"""
    # Execute the dynamic analysis code, passing in the system as part of globals
    exec_dynamic_code(analysis_code, globals())
