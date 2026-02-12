import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
import joblib
from pathlib import Path
from sklearn.preprocessing import StandardScaler
from torch.utils.data import DataLoader, TensorDataset

# TRAIN MLP FOR MALIGNANCY RISK
def train_risk_mlp(csv_files, save_dir):
    df_list = [pd.read_csv(f) for f in csv_files]
    df = pd.concat(df_list, ignore_index=True)

    # Only use useful numeric features
    X = df[["hu_mean", "hu_std", "long_axis_mm", "volume_mm3"]].values.astype(np.float32)

    # Create pseudo labels for Phase-1
    # Radiologist malignancy scores can replace this later
    y = (df["long_axis_mm"].values > 6).astype(np.float32)

    # Normalize features
    scaler = StandardScaler()
    X = scaler.fit_transform(X)
    
    # Save scaler
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(scaler, save_dir / "risk_scaler.pkl")

    X_t = torch.tensor(X)
    y_t = torch.tensor(y).unsqueeze(1)

    ds = TensorDataset(X_t, y_t)
    dl = DataLoader(ds, batch_size=32, shuffle=True)

    # Simple 2-layer MLP
    model = nn.Sequential(
        nn.Linear(4, 16),
        nn.ReLU(),
        nn.Linear(16, 8),
        nn.ReLU(),
        nn.Linear(8, 1),
        nn.Sigmoid()
    )

    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Train
    for epoch in range(10):
        for batch_x, batch_y in dl:
            optimizer.zero_grad()
            pred = model(batch_x)
            loss = criterion(pred, batch_y)
            loss.backward()
            optimizer.step()
        print(f"Epoch {epoch+1}/10 - Loss: {loss.item():.4f}")

    # Save model
    torch.save(model.state_dict(), save_dir / "risk_head.pth")
    print("Model saved:", save_dir / "risk_head.pth")

    return model
