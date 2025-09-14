# generative_core.py
#!/usr/bin/env python3
"""
Flora/OS Generative Core (v2.1 Final)
This script runs a robust biological simulation based on a prompt.json file.
It interprets L-System rules to generate complex geometry data and saves
it to a standard simulation state file.
"""
import argparse
import pickle
import json
import numpy as np

class LSystem:
    """A robust L-System interpreter."""
    def __init__(self, axiom, rules):
        self.axiom = axiom
        self.rules = rules
        self.state = axiom

    def iterate(self, n=1):
        for _ in range(n):
            new_state = ""
            for char in self.state:
                rule = self.rules.get(char)
                if isinstance(rule, str):
                    new_state += rule
                # This version simplifies probabilistic rules for stability
                elif isinstance(rule, list):
                     new_state += rule[0].get('successor', char)
                else:
                    new_state += char
            self.state = new_state
        return self.state

class Turtle:
    """A 3D turtle that generates valid curve data."""
    def __init__(self, angle=22.5):
        self.position = np.array([0.0, 0.0, 0.0])
        self.direction = np.array([0.0, 1.0, 0.0])
        self.up = np.array([0.0, 0.0, 1.0])
        self.angle = np.radians(angle)
        self.stack = []
        self.vertices = []
        self.curve_vertex_counts = []

    def execute(self, lsystem_string, step_length=0.1):
        current_curve_points = []
        
        # Start the first point
        self.vertices.append(list(self.position))
        current_curve_points.append(len(self.vertices) - 1)

        for command in lsystem_string:
            if command == 'F':
                self.position += self.direction * step_length
                self.vertices.append(list(self.position))
                current_curve_points.append(len(self.vertices) - 1)
            elif command in "+-&^\\/":
                self._rotate(command)
            elif command == '[':
                if len(current_curve_points) > 1:
                    self.curve_vertex_counts.append(len(current_curve_points))
                self.stack.append((self.position.copy(), self.direction.copy(), self.up.copy()))
                current_curve_points = [len(self.vertices) - 1] # Start new curve from current vertex
            elif command == ']':
                if len(current_curve_points) > 1:
                    self.curve_vertex_counts.append(len(current_curve_points))
                if self.stack:
                    self.position, self.direction, self.up = self.stack.pop()
                    self.vertices.append(list(self.position)) # Add a new vertex to start the new line segment
                    current_curve_points = [len(self.vertices) - 1]
                else:
                    current_curve_points = []

        if len(current_curve_points) > 1:
            self.curve_vertex_counts.append(len(current_curve_points))
            
        return self.vertices, self.curve_vertex_counts

    def _rotate(self, command):
        axis = None
        angle = self.angle
        if command == '+': axis = self.up
        elif command == '-': axis = -self.up
        elif command == '&': axis = np.cross(self.direction, self.up)
        elif command == '^': axis = -np.cross(self.direction, self.up)
        elif command == '\\': axis = self.direction
        elif command == '/': axis = -self.direction
        
        if axis is not None and np.linalg.norm(axis) > 0:
            axis = axis / np.linalg.norm(axis)
            cos_a = np.cos(angle)
            sin_a = np.sin(angle)
            self.direction = (self.direction * cos_a +
                            np.cross(axis, self.direction) * sin_a +
                            axis * np.dot(axis, self.direction) * (1 - cos_a))
            # Also rotate the 'up' vector to handle roll
            self.up = (self.up * cos_a +
                       np.cross(axis, self.up) * sin_a +
                       axis * np.dot(axis, self.up) * (1 - cos_a))


def run_simulation(prompt_file_path, output_state_path):
    print("--- Starting Flora/OS Generative Core (v2.1 Final)...---")
    with open(prompt_file_path, 'r') as f:
        prompt = json.load(f)
    print(f"Loading digital genome: {prompt['metadata']['simulation_name']}")

    lsystem_params = prompt['morphogenesis_engine']['l_system_parameters']
    lsystem = LSystem(lsystem_params['axiom'], lsystem_params['rules'])
    
    print("Simulating organism growth (5 iterations)...")
    final_string = lsystem.iterate(5)

    turtle = Turtle(angle=lsystem_params['angle_degrees'])
    points, curve_counts = turtle.execute(final_string)

    final_state = {
        'organism_geometry': { 'points': points, 'curveVertexCounts': curve_counts }
    }
    
    with open(output_state_path, 'wb') as f:
        pickle.dump(final_state, f)
    print("--- Simulation finished successfully. ---")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the Flora/OS Generative Core simulation.")
    parser.add_argument('--prompt_file', type=str, required=True)
    parser.add_argument('--output_state', type=str, required=True)
    args = parser.parse_args()
    run_simulation(args.prompt_file, args.output_state)

