# translate_to_usd.py
#!/usr/bin/env python3
"""
Flora/OS USD Translation Pipeline (Starter Kit Simulation)
This script represents the final stage of the Flora/OS data cascade: the
physical codification of the simulation's output into a 3D asset. It takes
the raw simulation state (.pkl file) and the original prompt (.json file)
as input to generate a Universal Scene Description ('.usda') file.
A core principle of the Flora/OS framework is to create self-contained,
reproducible scientific artifacts. To fulfill this, this script embeds the
entire content of the original 'prompt.json' (the genotype) as metadata
within the final .usda file (the phenotype). This creates an unbreakable,
auditable link from the final asset back to the exact parameters that
created it.
"""
import argparse
import pickle
import json
from datetime import datetime
def create_usda_content(simulation_state, biological_prompt):
"""Constructs the string content for a simple .usda file."""
# Escape triple quotes within the JSON string for safe embedding
prompt_string_escaped = json.dumps(biological_prompt, indent=2).replace('"""', '\\"\\"\\"')
# Get the Universal Taxonomic Identifier (UTI) for the prim path
uti = biological_prompt.get('metadata', {}).get('uti', 'UNKNOWN_UTI')
prim_path_name = uti.replace('.', '_').replace('-', '_')
# Construct the .usda file content as a multi-line string.
# This defines a simple scene with a single Cube prim.
usda_template = f'''#usda 1.0
(
doc = "Flora/OS Generated Organism"
upAxis = "Z"
metersPerUnit = 1.0
customData = {{
string generatedBy = "Flora/OS Starter Kit v1.0"
string generationDate = "{datetime.utcnow().isoformat()}Z"
}}
)
def Xform "FloraOrganism_{prim_path_name}"
{{
# --- Core Principle: Genotype embedded in Phenotype
# The full biological prompt is stored here as metadata. This makes
# the USD file a self-contained, reproducible artifact, fulfilling a
# foundational requirement of the Flora/OS framework.
custom string flora:biologicalPrompt = """{prompt_string_escaped}"""
def Cube "organism_geometry"
{{
double size = 2
color3f[] primvars:displayColor = [(0.4, 0.8, 0.2)]
}}
}}
'''
return usda_template
def translate_to_usd(state_file_path, prompt_file_path, output_usd_path):
"""Loads simulation state and prompt, then generates a .usda file."""
print("--- Starting translation to USD... ---")
print(f"Loading simulation state from: {state_file_path}")
with open(state_file_path, 'rb') as f:
state = pickle.load(f)
print(f"Loading original prompt for metadata from: {prompt_file_path}")
with open(prompt_file_path, 'r') as f:
prompt = json.load(f)
print("Generating .usda file content...")
usda_content = create_usda_content(state, prompt)
print(f"Saving physical phenotype to: {output_usd_path}")
with open(output_usd_path, 'w') as f:
f.write(usda_content)
print("--- Translation complete. ---")
if __name__ == '__main__':
parser = argparse.ArgumentParser(
description="Translate a Flora/OS simulation state to a USD file."
)
parser.add_argument(
'--state_file',
type=str,
required=True,
help='Path to the serialized simulation state file (.pkl).'
)
parser.add_argument(
'--prompt_file',
type=str,
required=True,
help='Path to the original Biological Prompt JSON file for metadata embedding.'
)
parser.add_argument(
'--output_usd',
type=str,
required=True,
help='Path for the output USD file (.usda).'
)
args = parser.parse_args()
translate_to_usd(args.state_file, args.prompt_file, args.output_usd)