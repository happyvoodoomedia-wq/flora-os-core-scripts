# translate_to_usd.py
#!/usr/bin/env python3
"""
Flora/OS USD Translation Pipeline (v2.2 - Final Syntax Fix)
This script translates L-System geometry into a syntactically perfect
.usda file compatible with strict online viewers.
"""
import argparse
import pickle
import json

def create_usda_content(simulation_state, biological_prompt):
    """Constructs a syntactically correct .usda file content string."""
    prompt_string_escaped = json.dumps(biological_prompt, indent=2).replace('"""', '\\"\\"\\"')
    uti = biological_prompt.get('metadata', {}).get('uti', 'UNKNOWN_UTI')
    prim_path_name = uti.replace('.', '_').replace('-', '_')

    geometry = simulation_state.get('organism_geometry', {})
    points = geometry.get('points', [])
    curve_counts = geometry.get('curveVertexCounts', [])

    if not points or not curve_counts:
        return f'#usda 1.0\n\ndef Xform "EmptyOrganism_{prim_path_name}"\n{{}}'

    # This formatting is critical for strict parsers.
    # Each point tuple is on its own line, with a comma.
    points_str_list = [f"            ({p[0]:.4f}, {p[1]:.4f}, {p[2]:.4f})" for p in points]
    points_str = ",\n".join(points_str_list)
    curve_vertex_counts_str = ", ".join(map(str, curve_counts))

    usda_template = f'''#usda 1.0
(
    upAxis = "Y"
    metersPerUnit = 0.05
)

def Xform "FloraOrganism_{prim_path_name}"
{{
    custom string flora:biologicalPrompt = """{prompt_string_escaped}"""

    def BasisCurves "organism_geometry"
    {{
        int[] curveVertexCounts = [{curve_vertex_counts_str}]
        point3f[] points = [
{points_str}
        ]
        uniform token type = "linear"
        
        float[] widths = [0.025] (
            interpolation = "uniform"
        )
        color3f[] primvars:displayColor = [(0.7, 0.85, 0.98)]
    }}
}}
'''
    return usda_template

def translate_to_usd(state_file_path, prompt_file_path, output_usd_path):
    print("--- Starting translation to USD (v2.2 Final)... ---")
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
    parser.add_argument('--state_file', type=str, required=True)
    parser.add_argument('--prompt_file', type=str, required=True)
    parser.add_argument('--output_usd', type=str, required=True)
    args = parser.parse_args()
    translate_to_usd(args.state_file, args.prompt_file, args.output_usd)

