{# =============================================================================
   Patient Report Template - Tamil (Phase-2)
   
   Purpose: Understandable by rural Tamil-speaking users
   Language: Tamil (தமிழ்)
   
   Updated: Feb 2026
   ============================================================================= #}
<!DOCTYPE html>
<html lang="ta">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>உங்கள் நுரையீரல் ஸ்கேன் முடிவுகள்</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Tamil:wght@400;600;700&display=swap');
    
    body {
      font-family: "Noto Sans Tamil", "Noto Sans", Arial, sans-serif;
      color: #1f2937;
      font-size: 15px;
      line-height: 1.8;
      margin: 0;
      padding: 0;
      background: #fff;
    }

    .container { max-width: 700px; margin: 0 auto; padding: 24px; }

    .header {
      text-align: center;
      padding: 20px 0;
      border-bottom: 3px solid #3b82f6;
      margin-bottom: 24px;
    }

    .header h1 { margin: 0; font-size: 26px; color: #1e3a5f; }
    .header .subtitle { color: #6b7280; font-size: 14px; margin-top: 6px; }

    .patient-info {
      background: #f0f9ff;
      padding: 12px 16px;
      border-radius: 8px;
      margin-top: 12px;
      font-size: 13px;
    }

    .card {
      background: #fff;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      padding: 20px;
      margin: 20px 0;
      box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    .card-title { font-size: 18px; color: #1e3a5f; margin: 0 0 12px 0; }

    .message-good {
      background: #ecfdf5;
      border: 1px solid #10b981;
      border-radius: 8px;
      padding: 16px;
      color: #065f46;
    }

    .message-concern {
      background: #fef3c7;
      border: 1px solid #f59e0b;
      border-radius: 8px;
      padding: 16px;
      color: #92400e;
    }

    .findings-table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 13px; }
    .findings-table th { text-align: left; padding: 10px 8px; background: #f8fafc; border-bottom: 2px solid #e2e8f0; }
    .findings-table td { padding: 12px 8px; border-bottom: 1px solid #f1f5f9; }

    .risk-label { display: inline-block; padding: 4px 12px; border-radius: 16px; font-weight: 600; font-size: 12px; }
    .risk-low { background: #d1fae5; color: #065f46; }
    .risk-moderate { background: #fef3c7; color: #92400e; }
    .risk-high { background: #fee2e2; color: #991b1b; }

    .next-steps { background: #eff6ff; border: 2px solid #3b82f6; }
    .steps-list { margin: 0; padding-left: 20px; }
    .steps-list li { margin: 12px 0; color: #1e40af; }

    .footer { margin-top: 30px; padding: 16px; background: #f9fafb; border-radius: 8px; font-size: 12px; color: #6b7280; text-align: center; }
  </style>
</head>
<body>
  <div class="container">

    <div class="header">
      <h1>🫁 உங்கள் நுரையீரல் ஸ்கேன் முடிவுகள்</h1>
      <div class="subtitle">உங்கள் மார்பு CT ஸ்கேன் பற்றிய எளிய சுருக்கம்</div>
      <div class="patient-info">
        <strong>ஸ்கேன் ID:</strong> {{ study_uid or study_id or 'N/A' }} &nbsp;|&nbsp;
        <strong>தேதி:</strong> {{ scan_date or 'N/A' }}
      </div>
    </div>

    <div class="card">
      <h2 class="card-title">📋 இந்த அறிக்கை என்ன காட்டுகிறது</h2>
      <p>
        இந்த அறிக்கை உங்கள் சமீபத்திய மார்பு CT ஸ்கேன் முடிவுகளை எளிய வார்த்தைகளில் விளக்குகிறது. 
        எங்கள் AI அமைப்பு உங்கள் நுரையீரல்களை பகுப்பாய்வு செய்து உங்கள் மருத்துவர் உங்கள் 
        ஆரோக்கியத்தை நன்றாக புரிந்துகொள்ள உதவும் முக்கியமான விவரங்களைக் கண்டறிந்தது.
      </p>
    </div>

    <div class="card">
      <h2 class="card-title">🔍 நாங்கள் என்ன கண்டறிந்தோம்</h2>
      
      {% set nodule_count = nodules|length if nodules else 0 %}
      {% set high_risk = high_risk_count or 0 %}
      
      {% if nodule_count == 0 %}
        <div class="message-good">
          ✓ உங்கள் நுரையீரல்களில் கவலைக்குரிய பகுதிகள் (நோடூல்கள்) எதுவும் கண்டறியப்படவில்லை. 
          இது நல்ல செய்தி! வழக்கமான உடல்நல பரிசோதனைகளை தொடருங்கள்.
        </div>
      {% elif high_risk == 0 %}
        <div class="message-good">
          ✓ உங்கள் நுரையீரல்களில் {{ nodule_count }} சிறிய புள்ளி(கள்) கண்டறியப்பட்டன, ஆனால் அவை குறைந்த ஆபத்துள்ளதாக தெரிகிறது. 
          அவற்றை கண்காணிக்க உங்கள் மருத்துவர் வழக்கமான பின்தொடர் ஸ்கேன்களை பரிந்துரைக்கலாம்.
        </div>
      {% else %}
        <div class="message-concern">
          ⚠ உங்கள் நுரையீரல்களில் {{ nodule_count }} புள்ளி(கள்) கண்டறியப்பட்டன. 
          அவற்றில் {{ high_risk }} உங்கள் மருத்துவரின் கவனம் தேவை.
          இந்த அறிக்கையை விரைவில் உங்கள் மருத்துவரிடம் காட்டுங்கள்.
        </div>
      {% endif %}

      {% if nodules and nodule_count > 0 %}
      <h3 style="font-size: 15px; margin-top: 20px;">கண்டுபிடிப்புகளின் விவரங்கள்</h3>
      <table class="findings-table">
        <thead>
          <tr><th>புள்ளி #</th><th>அளவு</th><th>ஆபத்து நிலை</th><th>இதன் பொருள்</th></tr>
        </thead>
        <tbody>
          {% for n in nodules[:10] %}
          {% set prob = n.prob_malignant if n.prob_malignant is defined else (n.p_malignant if n.p_malignant is defined else 0) %}
          {% set risk_label = "அதிகம்" if prob >= 0.7 else ("நடுத்தரம்" if prob >= 0.4 else "குறைவு") %}
          {% set risk_class = "high" if prob >= 0.7 else ("moderate" if prob >= 0.4 else "low") %}
          <tr>
            <td>#{{ n.id }}</td>
            <td>{{ n.long_axis_mm or 'சிறிய' }} mm</td>
            <td><span class="risk-label risk-{{ risk_class }}">{{ risk_label }}</span></td>
            <td>{% if prob >= 0.7 %}உங்கள் மருத்துவர் கவனமாக மதிப்பாய்வு செய்ய வேண்டும்.
            {% elif prob >= 0.4 %}பின்தொடர் ஸ்கேன் தேவைப்படலாம்.
            {% else %}சாதாரணமாக தெரிகிறது.{% endif %}</td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
      {% endif %}
    </div>

    <div class="card next-steps">
      <h2 class="card-title">👉 அடுத்ததாக என்ன செய்வது</h2>
      {% if high_risk and high_risk > 0 %}
      <ol class="steps-list">
        <li><strong>இந்த அறிக்கையை</strong> உடனடியாக உங்கள் மருத்துவரிடம் காட்டுங்கள்.</li>
        <li><strong>பயப்படாதீர்கள்</strong> — பல புள்ளிகள் தீங்கற்றவையாக மாறும்.</li>
        <li><strong>உங்கள் மருத்துவரிடம் கேளுங்கள்</strong> மேலும் பரிசோதனைகள் தேவையா என்று.</li>
        <li><strong>உங்கள் கேள்விகளை எழுதுங்கள்</strong> மருத்துவரிடம் கேட்க.</li>
      </ol>
      {% else %}
      <ol class="steps-list">
        <li><strong>இந்த அறிக்கையை</strong> உங்கள் அடுத்த வருகையில் மருத்துவரிடம் காட்டுங்கள்.</li>
        <li><strong>வழக்கமான பரிசோதனைகளை தொடருங்கள்</strong>.</li>
        <li><strong>ஆரோக்கியமான பழக்கங்களை பராமரியுங்கள்</strong> — புகைபிடிப்பதை தவிர்க்கவும்.</li>
      </ol>
      {% endif %}
    </div>

    <div class="footer">
      <p><strong>முக்கியமானது:</strong> இந்த அறிக்கை தகவலுக்காக மட்டுமே மற்றும் மருத்துவர் ஆலோசனைக்கு மாற்றாக அல்ல.</p>
      <p>அறிக்கை உருவாக்கப்பட்டது: {{ generation_time or 'N/A' }} | HealthATM AI</p>
    </div>

  </div>
</body>
</html>
