# train_lndb_mlp.py
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import torch, torch.nn as nn, torch.optim as optim, joblib
from torch.utils.data import DataLoader, TensorDataset

def train_lndb_mlp(features_csv, save_dir, epochs=12):
    df = pd.read_csv(features_csv)
    X = df[["hu_mean","hu_std","long_axis_mm","volume_mm3"]].fillna(0).values.astype(np.float32)
    y = df["malignancy"].astype(np.float32).values.reshape(-1,1)

    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)

    X_t = torch.tensor(Xs, dtype=torch.float32)
    y_t = torch.tensor(y, dtype=torch.float32)

    ds = TensorDataset(X_t, y_t)
    dl = DataLoader(ds, batch_size=64, shuffle=True)

    model = nn.Sequential(
        nn.Linear(4, 32),
        nn.ReLU(),
        nn.Dropout(0.2),
        nn.Linear(32, 16),
        nn.ReLU(),
        nn.Dropout(0.1),
        nn.Linear(16, 1),
        nn.Sigmoid()
    )

    criterion = nn.BCELoss()
    opt = optim.Adam(model.parameters(), lr=1e-3)

    for ep in range(epochs):
        total_loss = 0.0
        for xb, yb in dl:
            opt.zero_grad()
            pred = model(xb)
            loss = criterion(pred, yb)
            loss.backward()
            opt.step()
            total_loss += loss.item()
        print(f"Epoch {ep+1}/{epochs} - Loss: {total_loss/len(dl):.4f}")

    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), save_dir / "risk_head.pth")
    joblib.dump(scaler, save_dir / "risk_scaler.pkl")
    print("Saved model & scaler to", save_dir)
    return model
