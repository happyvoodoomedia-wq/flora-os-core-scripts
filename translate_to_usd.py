# translate_to_usd.py
#!/usr/bin/env python3
"""
Flora/OS USD Translation Pipeline (v4.1 - Definitive Final)
This script uses the official OpenUSD library (pxr) to create a robust,
binary .usdc file from the simulation state. This version contains the
final bug fix for attribute setting.
"""
import argparse
import pickle
import json

def translate_to_usdc(state_file_path, prompt_file_path, output_usd_path):
    try:
        from pxr import Usd, UsdGeom, Gf, Sdf, Vt
    except ImportError:
        print("\n!!! CRITICAL ERROR: OpenUSD library (pxr) not found. !!!")
        with open(output_usd_path, 'w') as f:
            f.write("# FAILED: OpenUSD library not found.")
        return

    print("--- Starting translation to USDC (v4.1 Definitive)... ---")
    try:
        with open(state_file_path, 'rb') as f:
            state = pickle.load(f)
        with open(prompt_file_path, 'r') as f:
            prompt = json.load(f)

        stage = Usd.Stage.CreateNew(output_usd_path)
        UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y)

        uti = prompt.get('metadata', {}).get('uti', 'UNKNOWN_UTI')
        prim_path = f"/FloraOrganism_{uti.replace('.', '_').replace('-', '_')}"
        
        organism_prim = UsdGeom.Xform.Define(stage, prim_path).GetPrim()
        organism_prim.CreateAttribute("flora:biologicalPrompt", Sdf.ValueTypeNames.String).Set(json.dumps(prompt, indent=2))

        geometry = state.get('organ_geometry', {})
        points = geometry.get('points', [])
        curve_counts = geometry.get('curveVertexCounts', [])

        if points and curve_counts:
            curves_geom = UsdGeom.BasisCurves.Define(stage, f"{prim_path}/organism_geometry")
            curves_geom.GetPointsAttr().Set(Vt.Vec3fArray([Gf.Vec3f(p) for p in points]))
            curves_geom.GetCurveVertexCountsAttr().Set(Vt.IntArray(curve_counts))
            curves_geom.GetTypeAttr().Set(UsdGeom.Tokens.linear)
            
            # This is the corrected, simpler way to set the width
            curves_geom.CreateWidthsAttr(Vt.FloatArray([0.025]))
            
            color_attr = curves_geom.CreateDisplayColorAttr()
            color_attr.Set(Vt.Vec3fArray([Gf.Vec3f(0.7, 0.85, 0.98)]))
        else:
            print("Warning: No geometry data found in simulation state.")

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
