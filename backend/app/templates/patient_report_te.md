{# =============================================================================
   Patient Report Template - Telugu (Phase-2)
   
   Purpose: Understandable by rural Telugu-speaking users
   Language: Telugu (తెలుగు)
   
   Updated: Feb 2026
   ============================================================================= #}
<!DOCTYPE html>
<html lang="te">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>మీ ఊపిరితిత్తుల స్కాన్ ఫలితాలు</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Telugu:wght@400;600;700&display=swap');
    
    body {
      font-family: "Noto Sans Telugu", "Noto Sans", Arial, sans-serif;
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

    .card-title {
      font-size: 18px;
      color: #1e3a5f;
      margin: 0 0 12px 0;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .message-good {
      background: #ecfdf5;
      border: 1px solid #10b981;
      border-radius: 8px;
      padding: 16px;
      color: #065f46;
      font-size: 15px;
    }

    .message-concern {
      background: #fef3c7;
      border: 1px solid #f59e0b;
      border-radius: 8px;
      padding: 16px;
      color: #92400e;
      font-size: 15px;
    }

    .findings-table { width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 13px; }
    .findings-table th { text-align: left; padding: 10px 8px; background: #f8fafc; border-bottom: 2px solid #e2e8f0; }
    .findings-table td { padding: 12px 8px; border-bottom: 1px solid #f1f5f9; }

    .risk-label { display: inline-block; padding: 4px 12px; border-radius: 16px; font-weight: 600; font-size: 12px; }
    .risk-low { background: #d1fae5; color: #065f46; }
    .risk-moderate { background: #fef3c7; color: #92400e; }
    .risk-high { background: #fee2e2; color: #991b1b; }

    .next-steps { background: #eff6ff; border: 2px solid #3b82f6; }
    .next-steps .card-title { color: #1d4ed8; }
    .steps-list { margin: 0; padding-left: 20px; }
    .steps-list li { margin: 12px 0; color: #1e40af; }

    .footer {
      margin-top: 30px;
      padding: 16px;
      background: #f9fafb;
      border-radius: 8px;
      font-size: 12px;
      color: #6b7280;
      text-align: center;
    }

    @media print { .container { max-width: 100%; } .card { break-inside: avoid; } }
  </style>
</head>
<body>
  <div class="container">

    <div class="header">
      <h1>🫁 మీ ఊపిరితిత్తుల స్కాన్ ఫలితాలు</h1>
      <div class="subtitle">మీ ఛాతీ CT స్కాన్ యొక్క సరళమైన సారాంశం</div>
      <div class="patient-info">
        <strong>స్కాన్ ID:</strong> {{ study_uid or study_id or 'N/A' }} &nbsp;|&nbsp;
        <strong>తేదీ:</strong> {{ scan_date or 'N/A' }}
      </div>
    </div>

    <div class="card">
      <h2 class="card-title"><span class="icon">📋</span> ఈ నివేదిక ఏమి చూపిస్తుంది</h2>
      <p>
        ఈ నివేదిక మీ ఇటీవలి ఛాతీ CT స్కాన్ ఫలితాలను సరళ పదాలలో వివరిస్తుంది. 
        మా AI వ్యవస్థ మీ ఊపిరితిత్తులను విశ్లేషించి మీ వైద్యుడికి మీ ఆరోగ్యాన్ని 
        బాగా అర్థం చేసుకోవడంలో సహాయపడే ముఖ్యమైన వివరాలను కనుగొంది.
      </p>
    </div>

    <div class="card">
      <h2 class="card-title"><span class="icon">🔍</span> మేము ఏమి కనుగొన్నాము</h2>
      
      {% set nodule_count = nodules|length if nodules else 0 %}
      {% set high_risk = high_risk_count or 0 %}
      
      {% if nodule_count == 0 %}
        <div class="message-good">
          ✓ మీ ఊపిరితిత్తులలో ఆందోళనకరమైన ప్రాంతాలు (నోడ్యూల్స్) ఏవీ కనుగొనబడలేదు. 
          ఇది మంచి వార్త! సాధారణ ఆరోగ్య తనిఖీలను కొనసాగించండి.
        </div>
      {% elif high_risk == 0 %}
        <div class="message-good">
          ✓ మేము మీ ఊపిరితిత్తులలో {{ nodule_count }} చిన్న మచ్చ(లు) కనుగొన్నాము, కానీ అవి తక్కువ ప్రమాదకరంగా కనిపిస్తున్నాయి. 
          వాటిని పర్యవేక్షించడానికి మీ వైద్యుడు సాధారణ ఫాలో-అప్ స్కాన్‌లను సూచించవచ్చు.
        </div>
      {% else %}
        <div class="message-concern">
          ⚠ మేము మీ ఊపిరితిత్తులలో {{ nodule_count }} మచ్చ(లు) కనుగొన్నాము. 
          వాటిలో {{ high_risk }} మీ వైద్యుడి దృష్టి అవసరం.
          దయచేసి ఈ నివేదికను వీలైనంత త్వరగా మీ వైద్యుడికి చూపించండి.
        </div>
      {% endif %}

      {% if nodules and nodule_count > 0 %}
      <h3 style="font-size: 15px; margin-top: 20px; color: #374151;">కనుగొన్న వివరాలు</h3>
      <table class="findings-table">
        <thead>
          <tr>
            <th>మచ్చ #</th>
            <th>పరిమాణం</th>
            <th>ప్రమాద స్థాయి</th>
            <th>దీని అర్థం</th>
          </tr>
        </thead>
        <tbody>
          {% for n in nodules[:10] %}
          {% set prob = n.prob_malignant if n.prob_malignant is defined else (n.p_malignant if n.p_malignant is defined else 0) %}
          {% set risk_label = "ఎక్కువ" if prob >= 0.7 else ("మధ్యస్థ" if prob >= 0.4 else "తక్కువ") %}
          {% set risk_class = "high" if prob >= 0.7 else ("moderate" if prob >= 0.4 else "low") %}
          <tr>
            <td>#{{ n.id }}</td>
            <td>{{ n.long_axis_mm or 'చిన్న' }} mm</td>
            <td><span class="risk-label risk-{{ risk_class }}">{{ risk_label }}</span></td>
            <td>
              {% if prob >= 0.7 %}మీ వైద్యుడు దీన్ని జాగ్రత్తగా సమీక్షించాలి.
              {% elif prob >= 0.4 %}ఫాలో-అప్ స్కాన్ అవసరం కావచ్చు.
              {% else %}సాధారణంగా కనిపిస్తుంది. సాధారణ తనిఖీలు సూచించబడతాయి.{% endif %}
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
      {% endif %}
    </div>

    <div class="card next-steps">
      <h2 class="card-title"><span class="icon">👉</span> తదుపరి ఏమి చేయాలి</h2>
      
      {% if high_risk and high_risk > 0 %}
      <ol class="steps-list">
        <li><strong>ఈ నివేదికను వీలైనంత త్వరగా</strong> మీ వైద్యుడికి చూపించండి.</li>
        <li><strong>భయపడకండి</strong> — చాలా మచ్చలు హానికరం కానివిగా తేలుతాయి.</li>
        <li><strong>మీ వైద్యుడిని అడగండి</strong> మీకు మరిన్ని పరీక్షలు లేదా ఫాలో-అప్ స్కాన్ అవసరమా అని.</li>
        <li><strong>మీ ప్రశ్నలను రాయండి</strong> మీరు వైద్యుడిని అడగాలనుకునేవి.</li>
      </ol>
      {% else %}
      <ol class="steps-list">
        <li><strong>ఈ నివేదికను</strong> మీ తదుపరి సందర్శనలో మీ వైద్యుడికి చూపించండి.</li>
        <li><strong>సాధారణ తనిఖీలను కొనసాగించండి</strong> మీ వైద్యుడు సూచించినట్లు.</li>
        <li><strong>ఆరోగ్యకరమైన అలవాట్లను కొనసాగించండి</strong> — ధూమపానం మానుకోండి మరియు చురుకుగా ఉండండి.</li>
      </ol>
      {% endif %}
    </div>

    <div class="footer">
      <p><strong>ముఖ్యమైనది:</strong> ఈ నివేదిక సమాచారం కోసం మాత్రమే మరియు మీ వైద్యుడి సలహాకు ప్రత్యామ్నాయం కాదు.</p>
      <p>నివేదిక రూపొందించబడింది: {{ generation_time or 'N/A' }} | హెల్త్ATM AI</p>
    </div>

  </div>
</body>
</html>
