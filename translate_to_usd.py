# translate_to_usd.py
#!/usr/bin/env python3
"""
Flora/OS USD Translation Pipeline (v1.2 - L-System Enabled)
This script translates the final state of a simulation, including L-System
geometry (vertices and edges), into a valid .usda file using BasisCurves.
"""
import argparse
import pickle
import json
from datetime import datetime

def create_usda_content(simulation_state, biological_prompt):
    """Constructs the string content for a .usda file with BasisCurves."""
    prompt_string_escaped = json.dumps(biological_prompt, indent=2).replace('"""', '\\"\\"\\"')
    uti = biological_prompt.get('metadata', {}).get('uti', 'UNKNOWN_UTI')
    prim_path_name = uti.replace('.', '_').replace('-', '_')

    # --- Extract geometry from the simulation state ---
    geometry = simulation_state.get('organism_geometry', {})
    vertices = geometry.get('vertices', [[0,0,0]])
    edges = geometry.get('edges', [])

    # Format vertices for USD
    points_str = ", ".join([f"({v[0]:.4f}, {v[1]:.4f}, {v[2]:.4f})" for v in vertices])
    
    # BasisCurves requires a list of how many vertices are in each curve.
    # For our simple lines, each "curve" has 2 vertices.
    curve_vertex_counts_str = ", ".join(["2"] * len(edges))

    usda_template = f'''#usda 1.0
(
    upAxis = "Y"
    metersPerUnit = 1.0
)

def Xform "FloraOrganism_{prim_path_name}"
{{
    custom string flora:biologicalPrompt = """{prompt_string_escaped}"""

    def BasisCurves "organism_geometry"
    {{
        int[] curveVertexCounts = [{curve_vertex_counts_str}]
        point3f[] points = [{points_str}]
        uniform token type = "linear"
        
        uniform float[] widths = [0.02]
        color3f[] primvars:displayColor = [(0.6, 0.75, 0.9)]
    }}
}}
'''
    return usda_template

def translate_to_usd(state_file_path, prompt_file_path, output_usd_path):
    """Loads state and prompt, then generates a valid .usda file."""
    print("--- Starting translation to USD (v1.2 L-System)... ---")
    try:
        with open(state_file_path, 'rb') as f:
            state = pickle.load(f)
        with open(prompt_file_path, 'r') as f:
            prompt = json.load(f)
            
        usda_content = create_usda_content(state, prompt)
        
        with open(output_usd_path, 'w') as f:
            f.write(usda_content)
        print(f"--- Translation complete. Valid USD file saved to: {output_usd_path} ---")
        
    except Exception as e:
        print(f"!!! An error occurred during translation: {e}")
        with open(output_usd_path, 'w') as f:
            f.write(f"# FAILED to generate USD. Error: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Translate a Flora/OS simulation state to a USD file.")
    parser.add_argument('--state_file', type=str, required=True, help='Path to the serialized simulation state file (.pkl).')
    parser.add_argument('--prompt_file', type=str, required=True, help='Path to the original Biological Prompt JSON file for metadata.')
    parser.add_argument('--output_usd', type=str, required=True, help='Path for the output USD file (.usda).')
    args = parser.parse_args()
    translate_to_usd(args.state_file, args.prompt_file, args.output_usd)
