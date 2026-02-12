{# Patient Report - Marathi (मराठी) #}
<!DOCTYPE html>
<html lang="mr">
<head>
  <meta charset="UTF-8"/><title>फुफ्फुस स्कॅन निकाल</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;600&display=swap');
    body { font-family: "Noto Sans Devanagari", sans-serif; font-size: 15px; line-height: 1.8; padding: 24px; max-width: 700px; margin: auto; }
    .header { text-align: center; border-bottom: 3px solid #3b82f6; padding-bottom: 20px; }
    .header h1 { color: #1e3a5f; }
    .card { border: 1px solid #e5e7eb; border-radius: 12px; padding: 20px; margin: 20px 0; }
    .good { background: #ecfdf5; border-color: #10b981; color: #065f46; padding: 16px; border-radius: 8px; }
    .concern { background: #fef3c7; border-color: #f59e0b; color: #92400e; padding: 16px; border-radius: 8px; }
    table { width: 100%; border-collapse: collapse; }
    th { background: #f8fafc; padding: 10px; text-align: left; }
    td { padding: 12px; border-bottom: 1px solid #f1f5f9; }
    .low { background: #d1fae5; padding: 4px 12px; border-radius: 16px; }
    .moderate { background: #fef3c7; padding: 4px 12px; border-radius: 16px; }
    .high { background: #fee2e2; padding: 4px 12px; border-radius: 16px; }
    .next { background: #eff6ff; border: 2px solid #3b82f6; }
    .footer { text-align: center; color: #6b7280; margin-top: 30px; }
  </style>
</head>
<body>
  <div class="header"><h1>🫁 तुमचा फुफ्फुस स्कॅन निकाल</h1>
    <p><strong>स्कॅन ID:</strong> {{ study_uid or 'N/A' }} | <strong>तारीख:</strong> {{ scan_date or 'N/A' }}</p>
  </div>
  <div class="card">
    <h2>🔍 आम्हाला काय आढळले</h2>
    {% set nodule_count = nodules|length if nodules else 0 %}
    {% set high_risk = high_risk_count or 0 %}
    {% if nodule_count == 0 %}<div class="good">✓ कोणतेही चिंताजनक क्षेत्र आढळले नाही. चांगली बातमी!</div>
    {% elif high_risk == 0 %}<div class="good">✓ {{ nodule_count }} लहान डाग, कमी धोका.</div>
    {% else %}<div class="concern">⚠ {{ nodule_count }} डाग. {{ high_risk }} साठी डॉक्टरांचे लक्ष आवश्यक.</div>{% endif %}
    {% if nodules and nodule_count > 0 %}
    <table><thead><tr><th>#</th><th>आकार</th><th>धोका</th></tr></thead><tbody>
      {% for n in nodules[:10] %}
      {% set prob = n.p_malignant or 0 %}
      <tr><td>{{ n.id }}</td><td>{{ n.long_axis_mm or '-' }}mm</td>
      <td><span class="{% if prob >= 0.7 %}high{% elif prob >= 0.4 %}moderate{% else %}low{% endif %}">{% if prob >= 0.7 %}उच्च{% elif prob >= 0.4 %}मध्यम{% else %}कमी{% endif %}</span></td></tr>
      {% endfor %}
    </tbody></table>{% endif %}
  </div>
  <div class="card next"><h2>👉 पुढे काय करायचे</h2><ul><li>डॉक्टरांना दाखवा</li><li>नियमित तपासणी करा</li></ul></div>
  <div class="footer"><p>हा अहवाल केवळ माहितीसाठी आहे. | {{ generation_time or 'N/A' }}</p></div>
</body>
</html>
