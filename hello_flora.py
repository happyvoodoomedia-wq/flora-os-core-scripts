# hello_flora.py
import sys
import numpy as np
import torch
import dspy

try:
    from pxr import Usd, UsdGeom
    USD_AVAILABLE = True
except ImportError:
    USD_AVAILABLE = False
    print("Warning: OpenUSD (pxr) library not found. USD translation will not be functional.")

def run_verification():
    """Executes a series of checks to verify the Flora/OS development environment."""
    print("--- Flora/OS Environment Verification ---")
    print(f"Python Version: {sys.version}")
    try:
        a = np.array([1, 2, 3])
        assert a.shape == (3,)
        print(f"[*] NumPy verification successful. Version: {np.__version__}")
    except Exception as e:
        print(f"[FAIL] NumPy verification failed: {e}")
    try:
        t = torch.tensor([1, 2, 3])
        assert t.shape == (3,)
        print(f"[*] PyTorch verification successful. Version: {torch.__version__}")
    except Exception as e:
        print(f"[FAIL] PyTorch verification failed: {e}")
    if USD_AVAILABLE:
        try:
            stage = Usd.Stage.CreateInMemory()
            xform = UsdGeom.Xform.Define(stage, '/hello')
            sphere = UsdGeom.Sphere.Define(stage, '/hello/world')
            assert str(sphere.GetPath()) == '/hello/world'
            print(f"[*] OpenUSD verification successful. Prim created: {sphere.GetPath()}")
        except Exception as e:
            print(f"[FAIL] OpenUSD verification failed: {e}")
    else:
        print("[SKIP] OpenUSD verification skipped.")
    try:
        sig = dspy.Signature("question -> answer")
        assert isinstance(sig, dspy.Signature)
        print("[*] DSPy verification successful. Signature object created.")
    except Exception as e:
        print(f"[FAIL] DSPy verification failed: {e}")
    print("--- Verification Complete ---")

if __name__ == "__main__":
    run_verification()
