#!/usr/bin/env python3
"""
Enhanced Traffic Simulation with Callback Analysis, Timestamping, Batch Mode,
Structured Log Export, and Pluggable Vehicle Behaviors.
"""

import random
import time
import logging
import json
import csv
from typing import Callable, Optional, List, Dict
from dataclasses import dataclass

# ------------------------------------------------------------------------------
# Configure Logging
# ------------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)

# ------------------------------------------------------------------------------
# Vehicle & Behavior
# ------------------------------------------------------------------------------
class Vehicle:
    """Represents a vehicle with a unique ID, speed, position, and optional behavior."""
    def __init__(
        self,
        vehicle_id: str,
        speed: float = 0.0,          # km/h
        behavior: Optional[Callable[['Vehicle', float, float], None]] = None
    ):
        self.vehicle_id = vehicle_id
        self.speed = speed            # km/h
        self.position = 0.0           # km
        self.behavior = behavior      # Optional speed/position modifier

    def update(self, dt: float, sim_time: float) -> None:
        """
        Apply an optional behavior (e.g. acceleration or random slow‑down),
        then update position based on (possibly modified) speed.
        """
        if self.behavior:
            try:
                self.behavior(self, dt, sim_time)
            except Exception as e:
                logging.warning(f"Behavior error for {self.vehicle_id}: {e}")

        # position delta = (speed km/h) * (dt seconds) / 3600
        self.position += (self.speed / 3600.0) * dt

# ------------------------------------------------------------------------------
# Transponder
# ------------------------------------------------------------------------------
class Transponder:
    """Simulates a transponder attached to a vehicle."""
    def __init__(self, vehicle: Vehicle):
        self.vehicle = vehicle

    def transmit(self) -> Dict:
        """Return the current state of the vehicle."""
        return {
            "vehicle_id": self.vehicle.vehicle_id,
            "speed": round(self.vehicle.speed, 2),
            "position": round(self.vehicle.position, 3)
        }

# ------------------------------------------------------------------------------
# Traffic System
# ------------------------------------------------------------------------------
class TrafficSystem:
    """
    Manages vehicles, runs the simulation in batch or real‑time mode,
    timestamps every record, supports structured export, and callback analysis.
    """
    def __init__(
        self,
        write_log: bool = True,
        csv_filename: str = "data_log.csv",
        json_filename: str = "data_log.json"
    ):
        self.vehicles: List[Vehicle] = []
        self.transponders: List[Transponder] = []
        self.data_log: List[Dict] = []
        self.write_log = write_log
        self.csv_filename = csv_filename
        self.json_filename = json_filename

    def add_vehicle(self, vehicle: Vehicle) -> None:
        self.vehicles.append(vehicle)
        self.transponders.append(Transponder(vehicle))

    def update_system(self, dt: float, sim_time: float) -> None:
        """Update vehicle positions, collect and timestamp data, log at DEBUG level."""
        for v in self.vehicles:
            v.update(dt, sim_time)

        for t in self.transponders:
            record = t.transmit()
            record['time'] = sim_time
            self.data_log.append(record)
            logging.debug(f"Record: {record}")

    def simulate(
        self,
        duration: float,
        dt: float,
        realtime: bool = False
    ) -> None:
        """
        Run the simulation for `duration` seconds, in steps of `dt`.
        If realtime is False, runs as fast as possible.
        """
        steps = int(duration / dt)
        sim_time = 0.0

        logging.info(f"Starting simulation: duration={duration}s, dt={dt}s, realtime={realtime}")
        for _ in range(steps):
            self.update_system(dt, sim_time)
            if realtime:
                time.sleep(dt)
            sim_time += dt
        logging.info("Simulation complete.")

        if self.write_log:
            self._export_logs()

    def _export_logs(self) -> None:
        """Write data_log to CSV and JSON for structured analysis."""
        if not self.data_log:
            logging.warning("No data to export.")
            return

        # CSV export
        with open(self.csv_filename, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(
                csvfile,
                fieldnames=list(self.data_log[0].keys())
            )
            writer.writeheader()
            writer.writerows(self.data_log)
        logging.info(f"Data log written to CSV: {self.csv_filename}")

        # JSON export
        with open(self.json_filename, "w", encoding="utf-8") as jsonfile:
            json.dump(self.data_log, jsonfile, indent=2)
        logging.info(f"Data log written to JSON: {self.json_filename}")

    def analyze(self, callback: Callable[[Dict], None]) -> None:
        """
        Apply a user‑provided callback to each record in the data log.
        This is safer and more flexible than exec().
        """
        for record in self.data_log:
            try:
                callback(record)
            except Exception as e:
                logging.error(f"Analysis callback error: {e}")

# ------------------------------------------------------------------------------
# Example Behavior Function
# ------------------------------------------------------------------------------
def random_slowdown(vehicle: Vehicle, dt: float, sim_time: float) -> None:
    """
    Randomly adjust the vehicle's speed by ±5 km/h every 10 seconds of sim_time.
    """
    if int(sim_time) % 10 == 0 and sim_time > 0:
        change = random.uniform(-5, 5)
        vehicle.speed = max(0, vehicle.speed + change)

# ------------------------------------------------------------------------------
# Main: set up, simulate, and analyze
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    # Create the traffic system (logs will be exported)
    system = TrafficSystem()

    # Add vehicles with an optional behavior
    for i in range(3):
        v = Vehicle(
            vehicle_id=f"Vehicle-{i+1}",
            speed=random.randint(20, 60),
            behavior=random_slowdown
        )
        system.add_vehicle(v)

    # Run 5-second simulation in batch mode (fast)
    system.simulate(duration=5, dt=1, realtime=False)

    # Define a simple callback to flag speeding vehicles
    def speed_alert(record: Dict) -> None:
        if record["speed"] > 40:
            print(f"Alert: {record['vehicle_id']} is speeding at {record['speed']} km/h (t={record['time']}s)")

    # Analyze the collected data
    system.analyze(speed_alert)
