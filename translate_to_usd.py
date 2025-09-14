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

def translate_to_usdc(state_file_path, prompt_file_path, output_usd_path):
    try:
        # This library is the official tool from Pixar/Nvidia
        from pxr import Usd, UsdGeom, Gf, Sdf, Vt
    except ImportError:
        print("\n!!! CRITICAL ERROR: OpenUSD library (pxr) not found. !!!")
        print("The 'usd-exchange' package required for this script did not install correctly.")
        with open(output_usd_path, 'w') as f:
            f.write("# FAILED: OpenUSD library not found.")
        return

    print("--- Starting translation to USDC (v4.0 Final)... ---")
    try:
        with open(state_file_path, 'rb') as f:
            state = pickle.load(f)
        with open(prompt_file_path, 'r') as f:
            prompt = json.load(f)

        # Create a new, blank USD stage (the foundation of the file)
        stage = Usd.Stage.CreateNew(output_usd_path)
        UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)

        # Get metadata for naming
        uti = prompt.get('metadata', {}).get('uti', 'UNKNOWN_UTI')
        prim_path = f"/FloraOrganism_{uti.replace('.', '_').replace('-', '_')}"
        
        # Create the main container for the organism
        organism_prim = UsdGeom.Xform.Define(stage, prim_path).GetPrim()
        
        # Embed the entire prompt.json inside the file for scientific record
        organism_prim.CreateAttribute("flora:biologicalPrompt", Sdf.ValueTypeNames.String).Set(json.dumps(prompt, indent=2))

        # Get the geometry data from the simulation
        geometry = state.get('organism_geometry', {})
        points = geometry.get('points', [])
        curve_counts = geometry.get('curveVertexCounts', [])

        if points and curve_counts:
            # Create a "BasisCurves" object to hold the line-based geometry
            curves_geom = UsdGeom.BasisCurves.Define(stage, f"{prim_path}/organism_geometry")
            
            # Add the points and connection data using the library's specific data types
            curves_geom.GetPointsAttr().Set(Vt.Vec3fArray([Gf.Vec3f(p) for p in points]))
            curves_geom.GetCurveVertexCountsAttr().Set(Vt.IntArray(curve_counts))
            
            # Define properties of the curves
            curves_geom.GetTypeAttr().Set(UsdGeom.Tokens.linear)
            widths_attr = curves_geom.CreateWidthsAttr()
            widths_attr.Set(Vt.FloatArray([0.025]))
            widths_attr.SetInterpolation(UsdGeom.Tokens.uniform)
            color_attr = curves_geom.CreateDisplayColorAttr()
            color_attr.Set(Vt.Vec3fArray([Gf.Vec3f(0.7, 0.85, 0.98)]))
        else:
            print("Warning: No geometry data found in simulation state. The file will be valid but empty.")

        # Save the final, compiled binary file
        stage.GetRootLayer().Save()
        print(f"--- Translation complete. Valid USDC file saved to: {output_usd_path} ---")
            
    except Exception as e:
        print(f"!!! An error occurred during the translation process: {e}")
        with open(output_usd_path, 'w') as f:
            f.write(f"# FAILED to generate USDC. Error: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Translate a Flora/OS simulation state to a binary USDC file.")
    parser.add_argument('--prompt_file', type=str, required=True)
    parser.add_argument('--state_file', type=str, required=True)
    parser.add_argument('--output_usd', type=str, required=True)
    args = parser.parse_args()
    translate_to_usdc(args.state_file, args.prompt_file, args.output_usd)
