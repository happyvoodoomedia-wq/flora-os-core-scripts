# translate_to_usd.py
#!/usr/bin/env python3
"""
Flora/OS USD Translation Pipeline (Functional Version)
This script translates the final state of a simulation into a valid,
viewable .usda file with a simple geometric representation.
"""
import argparse
import pickle
import json
from datetime import datetime

def create_usda_content(simulation_state, biological_prompt):
    """Constructs the string content for a simple but valid .usda file."""
    prompt_string_escaped = json.dumps(biological_prompt, indent=2).replace('"""', '\\"\\"\\"')
    uti = biological_prompt.get('metadata', {}).get('uti', 'UNKNOWN_UTI')
    prim_path_name = uti.replace('.', '_').replace('-', '_')

    # --- Create a simple geometric representation from the genome ---
    # This is still a placeholder for a real L-System or NCA renderer,
    # but it generates a valid, viewable shape based on the genome.
    genome = simulation_state.get('champion_organism', {}).get('genome', [0.5] * 3)
    
    # Use genome values to define the shape's properties
    cube_size = 1.0 + (genome[0] * 1.5) # Size based on first gene
    stem_height = 1.5 + (genome[1] * 2.0) # Height based on second gene
    stem_radius = 0.1 + (genome[2] * 0.4) # Radius based on third gene
    
    # Use genome values to define color
    red = genome[3] % 1.0 if len(genome) > 3 else 0.4
    green = genome[4] % 1.0 if len(genome) > 4 else 0.8
    blue = genome[5] % 1.0 if len(genome) > 5 else 0.2
    
    usda_template = f'''#usda 1.0
(
    doc = "Flora/OS Generated Organism"
    upAxis = "Z"
    metersPerUnit = 1.0
)

def Xform "FloraOrganism_{prim_path_name}"
{{
    custom string flora:biologicalPrompt = """{prompt_string_escaped}"""

    def Cylinder "Stem"
    {{
        double height = {stem_height}
        double radius = {stem_radius}
        color3f[] primvars:displayColor = [(0.5, 0.35, 0.25)]
    }}

    def Cube "Foliage"
    {{
        double size = {cube_size}
        color3f[] primvars:displayColor = [({red}, {green}, {blue})]
        matrix4d xformOp:transform = ( (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, {stem_height}, 1) )
        uniform token[] xformOpOrder = ["xformOp:transform"]
    }}
}}
'''
    return usda_template

def translate_to_usd(state_file_path, prompt_file_path, output_usd_path):
    """Loads state and prompt, then generates a valid .usda file."""
    print("--- Starting translation to USD (v1.1 Functional)... ---")
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
        # Create an empty file to prevent download errors, but log the failure.
        with open(output_usd_path, 'w') as f:
            f.write(f"# FAILED to generate USD. Error: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Translate a Flora/OS simulation state to a USD file.")
    parser.add_argument('--state_file', type=str, required=True, help='Path to the serialized simulation state file (.pkl).')
    parser.add_argument('--prompt_file', type=str, required=True, help='Path to the original Biological Prompt JSON file for metadata.')
    parser.add_argument('--output_usd', type=str, required=True, help='Path for the output USD file (.usda).')
    args = parser.parse_args()
    translate_to_usd(args.state_file, args.prompt_file, args.output_usd)
