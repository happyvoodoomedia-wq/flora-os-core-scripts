# generative_core.py
#!/usr/bin/env python3
"""
Flora/OS Generative Core (v3.0 - Production Final)
"""
import argparse
import pickle
import json
import numpy as np

class LSystem:
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
                elif isinstance(rule, list) and rule:
                    new_state += rule[0].get('successor', char)
                else:
                    new_state += char
            self.state = new_state
        return self.state

class Turtle:
    def __init__(self, angle=22.5):
        self.position = np.array([0.0, 0.0, 0.0])
        self.direction = np.array([0.0, 1.0, 0.0])
        self.up = np.array([0.0, 0.0, 1.0])
        self.angle = np.radians(angle)
        self.stack = []
        self.all_points = []
        self.curve_vertex_counts = []
        self.point_map = {}

    def _get_point_index(self, pos):
        pos_tuple = tuple(np.round(pos, 5))
        if pos_tuple not in self.point_map:
            self.point_map[pos_tuple] = len(self.all_points)
            self.all_points.append(list(pos))
        return self.point_map[pos_tuple]

    def execute(self, lsystem_string, step_length=0.1):
        current_curve_indices = [self._get_point_index(self.position)]
        for command in lsystem_string:
            if command == 'F':
                self.position += self.direction * step_length
                current_curve_indices.append(self._get_point_index(self.position))
            elif command in "+-&^\\/":
                self._rotate(command)
            elif command == '[':
                if len(current_curve_indices) > 1:
                    self.curve_vertex_counts.append(len(current_curve_indices))
                self.stack.append((self.position.copy(), self.direction.copy(), self.up.copy()))
                current_curve_indices = [self._get_point_index(self.position)]
            elif command == ']':
                if len(current_curve_indices) > 1:
                    self.curve_vertex_counts.append(len(current_curve_indices))
                if self.stack:
                    self.position, self.direction, self.up = self.stack.pop()
                    current_curve_indices = [self._get_point_index(self.position)]
                else:
                    current_curve_indices = []
        if len(current_curve_indices) > 1:
            self.curve_vertex_counts.append(len(current_curve_indices))
        return self.all_points, self.curve_vertex_counts

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
            axis /= np.linalg.norm(axis)
            cos_a, sin_a = np.cos(angle), np.sin(angle)
            self.direction = (self.direction * cos_a + np.cross(axis, self.direction) * sin_a + axis * np.dot(axis, self.direction) * (1 - cos_a))
            self.up = (self.up * cos_a + np.cross(axis, self.up) * sin_a + axis * np.dot(axis, self.up) * (1 - cos_a))

def run_simulation(prompt_file_path, output_state_path):
    print("--- Starting Flora/OS Generative Core (v3.0 Final)...---")
    with open(prompt_file_path, 'r') as f:
        prompt = json.load(f)
    print(f"Loading digital genome: {prompt['metadata']['simulation_name']}")
    ls_params = prompt['morphogenesis_engine']['l_system_parameters']
    lsystem = LSystem(ls_params['axiom'], ls_params['rules'])
    print("Simulating organism growth (5 iterations)...")
    final_string = lsystem.iterate(5)
    turtle = Turtle(angle=ls_params['angle_degrees'])
    points, curve_counts = turtle.execute(final_string)
    final_state = {'organism_geometry': {'points': points, 'curveVertexCounts': curve_counts}}
    with open(output_state_path, 'wb') as f:
        pickle.dump(final_state, f)
    print("--- Simulation finished successfully. ---")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the Flora/OS Generative Core simulation.")
    parser.add_argument('--prompt_file', type=str, required=True)
    parser.add_argument('--output_state', type=str, required=True)
    args = parser.parse_args()
    run_simulation(args.prompt_file, args.output_state)
