# Q-MIGRATE — Quantum-Safe Migration Intelligence

## What it demonstrates
1. Cryptographic discovery from source/config files.
2. Risk scoring and migration prioritization.
3. Dependency / migration blast-radius visualization.
4. A small Qiskit quantum-circuit optimization demonstration.

## Run
```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

Then upload source/config files or use the included `sample_project/`.

## Important
This is a hackathon prototype. The risk model is intentionally transparent and should not be presented as an enterprise security product. Real deployments would ingest CMDB/asset criticality, ownership, data lifetime, certificate inventories, SBOM/CBOM data and dependency telemetry.

The quantum demo demonstrates a small circuit and should be evaluated against a classical baseline; do not claim quantum advantage without measured evidence.
