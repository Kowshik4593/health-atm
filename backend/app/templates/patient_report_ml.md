{# Patient Report Template - Malayalam (മലയാളം) #}
<!DOCTYPE html>
<html lang="ml">
<head>
  <meta charset="UTF-8"/>
  <title>നിങ്ങളുടെ ശ്വാസകോശ സ്കാൻ ഫലങ്ങൾ</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Malayalam:wght@400;600;700&display=swap');
    body { font-family: "Noto Sans Malayalam", Arial, sans-serif; color: #1f2937; font-size: 15px; line-height: 1.8; margin: 0; padding: 0; }
    .container { max-width: 700px; margin: 0 auto; padding: 24px; }
    .header { text-align: center; padding: 20px 0; border-bottom: 3px solid #3b82f6; margin-bottom: 24px; }
    .header h1 { margin: 0; font-size: 26px; color: #1e3a5f; }
    .patient-info { background: #f0f9ff; padding: 12px 16px; border-radius: 8px; margin-top: 12px; }
    .card { background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 20px; margin: 20px 0; }
    .message-good { background: #ecfdf5; border: 1px solid #10b981; padding: 16px; color: #065f46; border-radius: 8px; }
    .message-concern { background: #fef3c7; border: 1px solid #f59e0b; padding: 16px; color: #92400e; border-radius: 8px; }
    .findings-table { width: 100%; border-collapse: collapse; }
    .findings-table th { text-align: left; padding: 10px 8px; background: #f8fafc; }
    .findings-table td { padding: 12px 8px; border-bottom: 1px solid #f1f5f9; }
    .risk-low { background: #d1fae5; color: #065f46; padding: 4px 12px; border-radius: 16px; }
    .risk-moderate { background: #fef3c7; color: #92400e; padding: 4px 12px; border-radius: 16px; }
    .risk-high { background: #fee2e2; color: #991b1b; padding: 4px 12px; border-radius: 16px; }
    .next-steps { background: #eff6ff; border: 2px solid #3b82f6; }
    .steps-list li { margin: 12px 0; color: #1e40af; }
    .footer { margin-top: 30px; padding: 16px; background: #f9fafb; text-align: center; color: #6b7280; border-radius: 8px; }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>🫁 നിങ്ങളുടെ ശ്വാസകോശ സ്കാൻ ഫലങ്ങൾ</h1>
      <div class="patient-info">
        <strong>സ്കാൻ ID:</strong> {{ study_uid or study_id or 'N/A' }} | <strong>തീയതി:</strong> {{ scan_date or 'N/A' }}
      </div>
    </div>

    <div class="card">
      <h2>📋 ഈ റിപ്പോർട്ട് എന്താണ് കാണിക്കുന്നത്</h2>
      <p>ഈ റിപ്പോർട്ട് നിങ്ങളുടെ സമീപകാല നെഞ്ച് CT സ്കാൻ ഫലങ്ങൾ ലളിതമായ വാക്കുകളിൽ വിശദീകരിക്കുന്നു.</p>
    </div>

    <div class="card">
      <h2>🔍 ഞങ്ങൾ കണ്ടെത്തിയത്</h2>
      {% set nodule_count = nodules|length if nodules else 0 %}
      {% set high_risk = high_risk_count or 0 %}
      
      {% if nodule_count == 0 %}
        <div class="message-good">✓ നിങ്ങളുടെ ശ്വാസകോശങ്ങളിൽ ആശങ്കാജനകമായ പ്രദേശങ്ങളൊന്നും കണ്ടെത്തിയില്ല. ഇത് നല്ല വാർത്തയാണ്!</div>
      {% elif high_risk == 0 %}
        <div class="message-good">✓ {{ nodule_count }} ചെറിയ പുള്ളി(കൾ) കണ്ടെത്തി, പക്ഷേ അവ കുറഞ്ഞ അപകടസാധ്യതയുള്ളതായി തോന്നുന്നു.</div>
      {% else %}
        <div class="message-concern">⚠ {{ nodule_count }} പുള്ളി(കൾ) കണ്ടെത്തി. {{ high_risk }} എണ്ണത്തിന് നിങ്ങളുടെ ഡോക്ടറുടെ ശ്രദ്ധ ആവശ്യമാണ്.</div>
      {% endif %}

      {% if nodules and nodule_count > 0 %}
      <table class="findings-table">
        <thead><tr><th>പുള്ളി #</th><th>വലിപ്പം</th><th>അപകടസാധ്യത</th><th>അർത്ഥം</th></tr></thead>
        <tbody>
          {% for n in nodules[:10] %}
          {% set prob = n.prob_malignant if n.prob_malignant is defined else (n.p_malignant if n.p_malignant is defined else 0) %}
          {% set risk_label = "ഉയർന്നത്" if prob >= 0.7 else ("മിതമായ" if prob >= 0.4 else "കുറവ്") %}
          {% set risk_class = "high" if prob >= 0.7 else ("moderate" if prob >= 0.4 else "low") %}
          <tr>
            <td>#{{ n.id }}</td>
            <td>{{ n.long_axis_mm or 'ചെറിയ' }} mm</td>
            <td><span class="risk-{{ risk_class }}">{{ risk_label }}</span></td>
            <td>{% if prob >= 0.7 %}ഡോക്ടർ പരിശോധിക്കണം{% elif prob >= 0.4 %}ഫോളോ-അപ്പ് വേണ്ടിവരാം{% else %}സാധാരണമായി തോന്നുന്നു{% endif %}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
      {% endif %}
    </div>

    <div class="card next-steps">
      <h2>👉 അടുത്തതായി എന്ത് ചെയ്യണം</h2>
      <ol class="steps-list">
        <li>ഈ റിപ്പോർട്ട് നിങ്ങളുടെ ഡോക്ടറെ കാണിക്കുക</li>
        <li>പതിവ് പരിശോധനകൾ തുടരുക</li>
        <li>ആരോഗ്യകരമായ ശീലങ്ങൾ നിലനിർത്തുക</li>
      </ol>
    </div>

    <div class="footer">
      <p><strong>പ്രധാനം:</strong> ഈ റിപ്പോർട്ട് വിവരങ്ങൾക്ക് മാത്രമാണ്. ഡോക്ടറുടെ ഉപദേശത്തിന് പകരമല്ല.</p>
      <p>റിപ്പോർട്ട്: {{ generation_time or 'N/A' }} | HealthATM AI</p>
    </div>
  </div>
</body>
</html>
