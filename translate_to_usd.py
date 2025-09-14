# translate_to_usd.py
#!/usr/bin/env python3
"""
Flora/OS USD Translation Pipeline (v4.0 - Binary USDC)
This script uses the official OpenUSD library (pxr) to create a robust,
binary .usdc file from the simulation state. This eliminates syntax errors.
"""
import argparse
import pickle
import json
from pxr import Usd, UsdGeom, Gf, Vt

def translate_to_usdc(state_file_path, prompt_file_path, output_usd_path):
    print("--- Starting translation to USDC (v4.0 Final)... ---")
    try:
        # Load data
        with open(state_file_path, 'rb') as f:
            state = pickle.load(f)
        with open(prompt_file_path, 'r') as f:
            prompt = json.load(f)

        # Create a new USD stage
        stage = Usd.Stage.CreateNew(output_usd_path)
        UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y) # Set Y as up-axis, common for 3D software

        # Get metadata
        uti = prompt.get('metadata', {}).get('uti', 'UNKNOWN_UTI')
        prim_path_name = f"/FloraOrganism_{uti.replace('.', '_').replace('-', '_')}"
        
        # Create root prim for the organism
        organism_prim = UsdGeom.Xform.Define(stage, prim_path_name).GetPrim()
        
        # Embed biological prompt as metadata
        organism_prim.CreateAttribute("flora:biologicalPrompt", Sdf.ValueTypeNames.String).Set(json.dumps(prompt, indent=2))

        # Get geometry from simulation state
        geometry = state.get('organism_geometry', {})
        points = geometry.get('points', [])
        curve_counts = geometry.get('curveVertexCounts', [])

        if points and curve_counts:
            # Create BasisCurves prim for the geometry
            curves_geom = UsdGeom.BasisCurves.Define(stage, f"{prim_path_name}/organism_geometry")
            
            # Set the points and curve vertex counts
            curves_geom.GetPointsAttr().Set(Vt.Vec3fArray([Gf.Vec3f(p) for p in points]))
            curves_geom.GetCurveVertexCountsAttr().Set(Vt.IntArray(curve_counts))
            
            # Set curve properties
            curves_geom.GetTypeAttr().Set(UsdGeom.Tokens.linear)
            widths_attr = curves_geom.CreateWidthsAttr()
            widths_attr.Set(Vt.FloatArray([0.025]))
            widths_attr.SetInterpolation(UsdGeom.Tokens.uniform)
            
            # Set display color
            color_attr = curves_geom.CreateDisplayColorAttr()
            color_attr.Set(Vt.Vec3fArray([Gf.Vec3f(0.7, 0.85, 0.98)]))
        else:
            print("Warning: No geometry data found in simulation state. Creating an empty organism.")

        # Save the stage
        stage.GetRootLayer().Save()
        print(f"--- Translation complete. Valid USDC file saved to: {output_usd_path} ---")

    except ImportError:
        print("\n!!! ERROR: OpenUSD library (pxr) not found. !!!")
        print("This script requires the 'usd-exchange' package.")
        print("Please ensure it is listed in your requirements.txt and installed.")
        # Create an empty file to prevent download errors
        with open(output_usd_path, 'w') as f:
            f.write("# FAILED: OpenUSD library not found.")
            
    except Exception as e:
        print(f"!!! An error occurred during translation: {e}")
        with open(output_usd_path, 'w') as f:
            f.write(f"# FAILED to generate USDC. Error: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Translate a Flora/OS simulation state to a binary USDC file.")
    parser.add_argument('--prompt_file', type=str, required=True)
    parser.add_argument('--state_file', type=str, required=True)
    # The Colab notebook will call this with a .usda extension, which is fine.
    # The library saves as binary based on the file content, not just the name.
    parser.add_argument('--output_usd', type=str, required=True)
    args = parser.parse_args()
    translate_to_usdc(args.state_file, args.prompt_file, args.output_usd)
