{# Patient Report - Gujarati (ગુજરાતી) #}
<!DOCTYPE html>
<html lang="gu">
<head>
  <meta charset="UTF-8"/><title>ફેફસાં સ્કેન પરિણામો</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Gujarati:wght@400;600&display=swap');
    body { font-family: "Noto Sans Gujarati", sans-serif; font-size: 15px; line-height: 1.8; padding: 24px; max-width: 700px; margin: auto; }
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
  <div class="header"><h1>🫁 તમારા ફેફસાં સ્કેન પરિણામો</h1>
    <p><strong>સ્કેન ID:</strong> {{ study_uid or 'N/A' }} | <strong>તારીખ:</strong> {{ scan_date or 'N/A' }}</p>
  </div>
  <div class="card">
    <h2>🔍 અમને શું મળ્યું</h2>
    {% set nodule_count = nodules|length if nodules else 0 %}
    {% set high_risk = high_risk_count or 0 %}
    {% if nodule_count == 0 %}<div class="good">✓ કોઈ ચિંતાજનક વિસ્તારો મળ્યા નથી. સારા સમાચાર!</div>
    {% elif high_risk == 0 %}<div class="good">✓ {{ nodule_count }} નાના ડાઘ, ઓછું જોખમ.</div>
    {% else %}<div class="concern">⚠ {{ nodule_count }} ડાઘ. {{ high_risk }} માટે ડૉક્ટરની ધ્યાન જરૂરી.</div>{% endif %}
    {% if nodules and nodule_count > 0 %}
    <table><thead><tr><th>#</th><th>કદ</th><th>જોખમ</th></tr></thead><tbody>
      {% for n in nodules[:10] %}
      {% set prob = n.p_malignant or 0 %}
      <tr><td>{{ n.id }}</td><td>{{ n.long_axis_mm or '-' }}mm</td>
      <td><span class="{% if prob >= 0.7 %}high{% elif prob >= 0.4 %}moderate{% else %}low{% endif %}">{% if prob >= 0.7 %}ઉચ્ચ{% elif prob >= 0.4 %}મધ્યમ{% else %}ઓછું{% endif %}</span></td></tr>
      {% endfor %}
    </tbody></table>{% endif %}
  </div>
  <div class="card next"><h2>👉 આગળ શું કરવું</h2><ul><li>ડૉક્ટરને બતાવો</li><li>નિયમિત તપાસ કરાવો</li></ul></div>
  <div class="footer"><p>આ રિપોર્ટ માત્ર માહિતી માટે છે. | {{ generation_time or 'N/A' }}</p></div>
</body>
</html>
