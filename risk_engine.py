import pandas as pd

QUANTUM_VULNERABLE = {"RSA","ECC/ECDSA","ECDH","DH","DSA"}

def score_assets(df):
    df = df.copy()
    df["quantum_vulnerable"] = df["algorithm"].isin(QUANTUM_VULNERABLE)
    base = df["algorithm"].map({
        "RSA": 90, "ECC/ECDSA": 90, "ECDH": 95, "DH": 95, "DSA": 90,
        "AES": 25, "SHA-256": 15, "SHA-1": 55, "TLS": 35
    }).fillna(40)

    # Prototype enterprise-risk factors. In a real deployment these come from CMDB,
    # asset criticality, data lifetime, exposure and dependency telemetry.
    df["risk_score"] = base.astype(float)
    df.loc[df["quantum_vulnerable"], "risk_score"] += 5
    df["risk_score"] = df["risk_score"].clip(0,100).round(1)

    df["priority"] = pd.cut(
        df["risk_score"], bins=[-1,39,69,84,101],
        labels=["LOW","MEDIUM","HIGH","CRITICAL"]
    ).astype(str)

    def action(r):
        if r["algorithm"] in {"RSA","ECC/ECDSA","ECDH","DH","DSA"}:
            return "Inventory dependency → test PQC replacement → plan migration"
        if r["algorithm"] == "SHA-1":
            return "Retire legacy hash where feasible"
        return "Monitor and maintain crypto-agility"
    df["recommended_action"] = df.apply(action, axis=1)
    return df

def prioritize(df):
    return df.sort_values(["risk_score","quantum_vulnerable"], ascending=[False,False]).reset_index(drop=True)
