# backend-dinesh/ml/risk/predict_risk.py
import torch
import torch.nn as nn
import joblib
import numpy as np

class RiskHead:
    def __init__(self, model_path, scaler_path, device="cpu"):
        self.device = torch.device(device)
        # load scaler
        self.scaler = joblib.load(str(scaler_path))
        # define model architecture exactly as used in training
        self.model = nn.Sequential(
            nn.Linear(4, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(16, 1),
            nn.Sigmoid()
        ).to(self.device)

        state = torch.load(str(model_path), map_location=self.device)
        # if state is state_dict or entire object, handle both
        if isinstance(state, dict) and any(k.startswith("0.") or k.startswith("1.") for k in state.keys()):
            self.model.load_state_dict(state)
        else:
            # assume state is state_dict directly
            try:
                self.model.load_state_dict(state)
            except Exception:
                # try common key
                self.model.load_state_dict(state)
        self.model.eval()

    def _preprocess(self, feature_list):
        x = np.array(feature_list, dtype=np.float32).reshape(1, -1)
        # handle scaler robustly
        x_scaled = self.scaler.transform(x)
        return torch.tensor(x_scaled, dtype=torch.float32).to(self.device)

    def predict(self, feature_list):
        """Deterministic single prediction"""
        x_t = self._preprocess(feature_list)
        with torch.no_grad():
            self.model.eval()
            out = self.model(x_t).cpu().numpy().ravel()[0]
        # ensure float in [0,1]
        return float(max(0.0, min(1.0, float(out))))

    def predict_mc_dropout(self, feature_list, T=20):
        """
        Run T stochastic forward passes with dropout enabled.
        Returns (p_mean, entropy)
        """
        x_t = self._preprocess(feature_list)
        # enable dropout layers
        for m in self.model.modules():
            if isinstance(m, nn.Dropout):
                m.train()

        probs = []
        with torch.no_grad():
            for _ in range(int(T)):
                p = float(self.model(x_t).cpu().numpy().ravel()[0])
                # clip extreme values to avoid log(0)
                p = max(1e-9, min(1.0 - 1e-9, p))
                probs.append(p)

        # restore eval mode
        self.model.eval()

        probs = np.array(probs, dtype=np.float64)
        p_mean = float(np.clip(probs.mean(), 1e-9, 1.0 - 1e-9))
        entropy = float(-(p_mean * np.log(p_mean) + (1 - p_mean) * np.log(1 - p_mean)))
        return p_mean, entropy
