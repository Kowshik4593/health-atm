{# =============================================================================
   Patient Report Template - Kannada (Phase-2)
   Language: Kannada (ಕನ್ನಡ)
   Updated: Feb 2026
   ============================================================================= #}
<!DOCTYPE html>
<html lang="kn">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>ನಿಮ್ಮ ಶ್ವಾಸಕೋಶದ ಸ್ಕ್ಯಾನ್ ಫಲಿತಾಂಶಗಳು</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Kannada:wght@400;600;700&display=swap');
    body { font-family: "Noto Sans Kannada", Arial, sans-serif; color: #1f2937; font-size: 15px; line-height: 1.8; margin: 0; padding: 0; }
    .container { max-width: 700px; margin: 0 auto; padding: 24px; }
    .header { text-align: center; padding: 20px 0; border-bottom: 3px solid #3b82f6; margin-bottom: 24px; }
    .header h1 { margin: 0; font-size: 26px; color: #1e3a5f; }
    .patient-info { background: #f0f9ff; padding: 12px 16px; border-radius: 8px; margin-top: 12px; }
    .card { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 20px; margin: 20px 0; }
    .card-title { font-size: 18px; color: #1e3a5f; margin: 0 0 12px 0; }
    .message-good { background: #ecfdf5; border: 1px solid #10b981; border-radius: 8px; padding: 16px; color: #065f46; }
    .message-concern { background: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; padding: 16px; color: #92400e; }
    .findings-table { width: 100%; border-collapse: collapse; margin: 12px 0; }
    .findings-table th { text-align: left; padding: 10px 8px; background: #f8fafc; }
    .findings-table td { padding: 12px 8px; border-bottom: 1px solid #f1f5f9; }
    .risk-label { display: inline-block; padding: 4px 12px; border-radius: 16px; font-weight: 600; }
    .risk-low { background: #d1fae5; color: #065f46; }
    .risk-moderate { background: #fef3c7; color: #92400e; }
    .risk-high { background: #fee2e2; color: #991b1b; }
    .next-steps { background: #eff6ff; border: 2px solid #3b82f6; }
    .steps-list li { margin: 12px 0; color: #1e40af; }
    .footer { margin-top: 30px; padding: 16px; background: #f9fafb; border-radius: 8px; text-align: center; color: #6b7280; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🫁 ನಿಮ್ಮ ಶ್ವಾಸಕೋಶದ ಸ್ಕ್ಯಾನ್ ಫಲಿತಾಂಶಗಳು</h1>
      <div class="patient-info">
        <strong>ಸ್ಕ್ಯಾನ್ ID:</strong> {{ study_uid or study_id or 'N/A' }} | <strong>ದಿನಾಂಕ:</strong> {{ scan_date or 'N/A' }}
      </div>
    </div>

    <div class="card">
      <h2 class="card-title">📋 ಈ ವರದಿ ಏನು ತೋರಿಸುತ್ತದೆ</h2>
      <p>ಈ ವರದಿ ನಿಮ್ಮ ಇತ್ತೀಚಿನ ಎದೆ CT ಸ್ಕ್ಯಾನ್ ಫಲಿತಾಂಶಗಳನ್ನು ಸರಳ ಪದಗಳಲ್ಲಿ ವಿವರಿಸುತ್ತದೆ.</p>
    </div>

    <div class="card">
      <h2 class="card-title">🔍 ನಾವು ಏನು ಕಂಡುಕೊಂಡೆವು</h2>
      {% set nodule_count = nodules|length if nodules else 0 %}
      {% set high_risk = high_risk_count or 0 %}
      
      {% if nodule_count == 0 %}
        <div class="message-good">✓ ನಿಮ್ಮ ಶ್ವಾಸಕೋಶಗಳಲ್ಲಿ ಆತಂಕಕಾರಿ ಪ್ರದೇಶಗಳು ಕಂಡುಬಂದಿಲ್ಲ. ಇದು ಒಳ್ಳೆಯ ಸುದ್ದಿ!</div>
      {% elif high_risk == 0 %}
        <div class="message-good">✓ {{ nodule_count }} ಸಣ್ಣ ಚುಕ್ಕೆ(ಗಳು) ಕಂಡುಬಂದಿವೆ, ಆದರೆ ಅವು ಕಡಿಮೆ ಅಪಾಯದಂತೆ ಕಾಣುತ್ತವೆ.</div>
      {% else %}
        <div class="message-concern">⚠ {{ nodule_count }} ಚುಕ್ಕೆ(ಗಳು) ಕಂಡುಬಂದಿವೆ. {{ high_risk }} ಗೆ ನಿಮ್ಮ ವೈದ್ಯರ ಗಮನ ಅಗತ್ಯ.</div>
      {% endif %}

      {% if nodules and nodule_count > 0 %}
      <table class="findings-table">
        <thead><tr><th>ಚುಕ್ಕೆ #</th><th>ಗಾತ್ರ</th><th>ಅಪಾಯ ಮಟ್ಟ</th><th>ಅರ್ಥ</th></tr></thead>
        <tbody>
          {% for n in nodules[:10] %}
          {% set prob = n.prob_malignant if n.prob_malignant is defined else (n.p_malignant if n.p_malignant is defined else 0) %}
          {% set risk_label = "ಹೆಚ್ಚು" if prob >= 0.7 else ("ಮಧ್ಯಮ" if prob >= 0.4 else "ಕಡಿಮೆ") %}
          {% set risk_class = "high" if prob >= 0.7 else ("moderate" if prob >= 0.4 else "low") %}
          <tr>
            <td>#{{ n.id }}</td>
            <td>{{ n.long_axis_mm or 'ಸಣ್ಣ' }} mm</td>
            <td><span class="risk-label risk-{{ risk_class }}">{{ risk_label }}</span></td>
            <td>{% if prob >= 0.7 %}ವೈದ್ಯರು ಪರಿಶೀಲಿಸಬೇಕು{% elif prob >= 0.4 %}ಫಾಲೋ-ಅಪ್ ಬೇಕಾಗಬಹುದು{% else %}ಸಾಮಾನ್ಯವಾಗಿ ಕಾಣುತ್ತದೆ{% endif %}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
      {% endif %}
    </div>

    <div class="card next-steps">
      <h2 class="card-title">👉 ಮುಂದೆ ಏನು ಮಾಡಬೇಕು</h2>
      <ol class="steps-list">
        <li>ಈ ವರದಿಯನ್ನು ನಿಮ್ಮ ವೈದ್ಯರಿಗೆ ತೋರಿಸಿ</li>
        <li>ನಿಯಮಿತ ತಪಾಸಣೆಗಳನ್ನು ಮುಂದುವರಿಸಿ</li>
        <li>ಆರೋಗ್ಯಕರ ಅಭ್ಯಾಸಗಳನ್ನು ಕಾಪಾಡಿಕೊಳ್ಳಿ</li>
      </ol>
    </div>

    <div class="footer">
      <p><strong>ಮುಖ್ಯ:</strong> ಈ ವರದಿ ಮಾಹಿತಿಗಾಗಿ ಮಾತ್ರ. ವೈದ್ಯರ ಸಲಹೆಗೆ ಬದಲಿಯಲ್ಲ.</p>
      <p>ವರದಿ: {{ generation_time or 'N/A' }} | HealthATM AI</p>
    </div>
  </div>
</body>
</html>
