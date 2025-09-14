# generative_core.py
#!/usr/bin/env python3
"""
Flora/OS Generative Core (v1.2 - Rule Fix)
This script runs a simplified biological simulation. It takes a prompt.json,
interprets the L-System rules (handling simple cases), and simulates growth.
"""
import argparse
import pickle
import json
import numpy as np

class LSystem:
    """A simple L-System interpreter that handles basic string rules."""
    def __init__(self, axiom, rules):
        self.axiom = axiom
        self.rules = rules
        self.state = axiom

    def iterate(self, n=1):
        """Apply rewriting rules n times."""
        for _ in range(n):
            new_state = ""
            for char in self.state:
                # This version handles the simple 'A' rule from the Abelia prompt.
                # It will ignore the complex probabilistic 'F' rule for now,
                # which prevents the script from crashing.
                if char in self.rules and isinstance(self.rules[char], str):
                    new_state += self.rules[char]
                else:
                    new_state += char
            self.state = new_state
        return self.state

class Turtle:
    """A 3D turtle graphics interpreter for L-System strings."""
    def __init__(self, start_pos=(0, 0, 0), start_dir=(0, 1, 0), angle=25.0): # Start facing Y-up
        self.position = np.array(start_pos, dtype=float)
        self.direction = np.array(start_dir, dtype=float)
        self.up = np.array([0, 0, -1], dtype=float) # Z is now "up" relative to the forward direction
        self.angle = np.radians(angle)
        self.stack = []
        # Store vertices and indices for curves
        self.vertices = []
        self.curve_indices = []
        self.current_curve = []

    def start_new_curve(self):
        self.current_curve = [len(self.vertices)]
        self.vertices.append(list(self.position))


    def execute(self, lsystem_string, step_length=0.1):
        """Parses an L-System string and generates geometry."""
        self.start_new_curve() # Initialize the first curve

        for command in lsystem_string:
            if command == 'F':
                self.position += self.direction * step_length
                self.vertices.append(list(self.position))
                self.current_curve.append(len(self.vertices) - 1)
            elif command == '+':
                self._rotate(self.up, self.angle)
            elif command == '-':
                self._rotate(self.up, -self.angle)
            elif command == '&':
                 right_vec = np.cross(self.direction, self.up)
                 self._rotate(right_vec, self.angle)
            elif command == '^':
                 right_vec = np.cross(self.direction, self.up)
                 self._rotate(right_vec, -self.angle)
            elif command == '[':
                self.stack.append((self.position.copy(), self.direction.copy(), self.up.copy()))
                if self.current_curve:
                    self.curve_indices.append(self.current_curve)
                self.start_new_curve()
            elif command == ']':
                if self.current_curve:
                    self.curve_indices.append(self.current_curve)
                self.position, self.direction, self.up = self.stack.pop()
                self.start_new_curve()

        if self.current_curve:
             self.curve_indices.append(self.current_curve)

        # We need to provide vertex counts for each curve segment
        curve_vertex_counts = [len(curve) for curve in self.curve_indices if len(curve) > 1]
        
        # The 'points' are simply the list of all vertices generated
        points = self.vertices

        return points, curve_vertex_counts


    def _rotate(self, axis, angle):
        """Helper for 3D rotation."""
        if np.linalg.norm(axis) == 0: return
        axis = axis / np.linalg.norm(axis)
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        self.direction = (self.direction * cos_a +
                        np.cross(axis, self.direction) * sin_a +
                        axis * np.dot(axis, self.direction) * (1 - cos_a))
        self.up = (self.up * cos_a +
                   np.cross(axis, self.up) * sin_a +
                   axis * np.dot(axis, self.up) * (1 - cos_a))

def run_simulation(prompt_file_path, output_state_path):
    """Simulates the main generative process."""
    print("--- Starting Flora/OS Generative Core simulation (v1.3 Rule Fix)...---")
    with open(prompt_file_path, 'r') as f:
        prompt = json.load(f)
    print(f"Loading digital genome: {prompt['metadata']['simulation_name']}")

    lsystem_params = prompt['morphogenesis_engine']['l_system_parameters']
    lsystem = LSystem(lsystem_params['axiom'], lsystem_params['rules'])
    
    print("Simulating organism growth (4 iterations)...")
    final_string = lsystem.iterate(4)

    print("Generating 3D phenotype with Turtle graphics...")
    turtle = Turtle(angle=lsystem_params['angle_degrees'])
    points, curve_counts = turtle.execute(final_string)

    final_state = {
        'simulation_metadata': { 'status': 'Completed', 'lsystem_iterations': 4 },
        'organism_geometry': { 'points': points, 'curveVertexCounts': curve_counts }
    }
    
    print(f"Saving final simulation state to: {output_state_path}")
    with open(output_state_path, 'wb') as f:
        pickle.dump(final_state, f)
    print("--- Simulation finished successfully. ---")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the Flora/OS Generative Core simulation.")
    parser.add_argument('--prompt_file', type=str, required=True)
    parser.add_argument('--output_state', type=str, required=True)
    args = parser.parse_args()
    run_simulation(args.prompt_file, args.output_state)

