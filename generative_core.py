# generative_core.py
#!/usr/bin/env python3
"""
Flora/OS Generative Core (v1.1 - L-System Enabled)
This script runs a simplified biological simulation. It takes a prompt.json,
interprets the L-System rules, and simulates the growth of the organism's
structure over a small number of iterations.
"""
import argparse
import pickle
import time
import random
import json
import numpy as np

# --- L-SYSTEM ENGINE ---
# This is the core logic that generates the organism's form.

class LSystem:
    """A simple L-System interpreter."""
    def __init__(self, axiom, rules):
        self.axiom = axiom
        self.rules = rules
        self.state = axiom

    def iterate(self, n=1):
        """Apply the rewriting rules to the current state n times."""
        for _ in range(n):
            new_state = ""
            for char in self.state:
                # For this version, we handle simple rule replacement.
                # A full implementation would handle the probabilistic rules.
                if char in self.rules and isinstance(self.rules[char], str):
                    new_state += self.rules[char]
                else:
                    new_state += char
            self.state = new_state
        return self.state

class Turtle:
    """A 3D turtle graphics interpreter for L-System strings."""
    def __init__(self, start_pos=(0, 0, 0), start_dir=(0, 0, 1), angle=25.0):
        self.position = np.array(start_pos, dtype=float)
        self.direction = np.array(start_dir, dtype=float)
        self.up = np.array([0, 1, 0], dtype=float) # Y-up for standard 3D space
        self.angle = np.radians(angle)
        self.stack = []
        self.vertices = [list(self.position)]
        self.edges = []

    def execute(self, lsystem_string, step_length=0.1):
        """Parses an L-System string and generates geometry."""
        for command in lsystem_string:
            if command == 'F':
                start_vtx_idx = len(self.vertices) - 1
                self.position += self.direction * step_length
                self.vertices.append(list(self.position))
                end_vtx_idx = len(self.vertices) - 1
                self.edges.append((start_vtx_idx, end_vtx_idx))
            elif command == '+': # Turn left (yaw)
                self._rotate(self.up, self.angle)
            elif command == '-': # Turn right (yaw)
                self._rotate(self.up, -self.angle)
            elif command == '&': # Pitch down
                right_vec = np.cross(self.direction, self.up)
                self._rotate(right_vec, self.angle)
            elif command == '^': # Pitch up
                right_vec = np.cross(self.direction, self.up)
                self._rotate(right_vec, -self.angle)
            elif command == '[':
                self.stack.append((self.position.copy(), self.direction.copy(), self.up.copy()))
            elif command == ']':
                self.position, self.direction, self.up = self.stack.pop()
                self.vertices.append(list(self.position))
        return self.vertices, self.edges

    def _rotate(self, axis, angle):
        """Helper for 3D rotation."""
        axis = axis / np.linalg.norm(axis)
        cos_a = np.cos(angle)
        sin_a = np.sin(angle)
        self.direction = (self.direction * cos_a +
                        np.cross(axis, self.direction) * sin_a +
                        axis * np.dot(axis, self.direction) * (1 - cos_a))

def run_simulation(prompt_file_path, output_state_path):
    """Simulates the main generative process."""
    print("--- Starting Flora/OS Generative Core simulation (v1.1 L-System)...---")
    with open(prompt_file_path, 'r') as f:
        prompt = json.load(f)
    print(f"Loading digital genome: {prompt['metadata']['simulation_name']}")

    # 1. Initialize the L-System from the prompt
    lsystem_params = prompt['morphogenesis_engine']['l_system_parameters']
    axiom = lsystem_params['axiom']
    rules = lsystem_params['rules']
    angle = lsystem_params['angle_degrees']
    
    lsystem = LSystem(axiom, rules)
    
    # 2. Simulate growth (iterate the L-system)
    # A full simulation would be 500 generations. We do 4 iterations for a visible result.
    print("Simulating organism growth (4 iterations)...")
    final_string = lsystem.iterate(4)

    # 3. Use the Turtle to generate the 3D structure
    print("Generating 3D phenotype with Turtle graphics...")
    turtle = Turtle(angle=angle)
    vertices, edges = turtle.execute(final_string)

    # 4. Save the final state containing the geometry
    final_state = {
        'simulation_metadata': {
            'status': 'Completed',
            'lsystem_iterations': 4
        },
        'organism_geometry': {
            'vertices': vertices,
            'edges': edges
        }
    }
    
    print(f"Saving final simulation state to: {output_state_path}")
    with open(output_state_path, 'wb') as f:
        pickle.dump(final_state, f)
    print("--- Simulation finished successfully. ---")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the Flora/OS Generative Core simulation.")
    parser.add_argument('--prompt_file', type=str, required=True, help='Path to the Biological Prompt JSON file.')
    parser.add_argument('--output_state', type=str, required=True, help='Path to save the final simulation state (.pkl file).')
    args = parser.parse_args()
    run_simulation(args.prompt_file, args.output_state)
