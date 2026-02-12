{# =============================================================================
   Patient Report Template - Hindi (Phase-2)
   
   Purpose: Understandable by rural / non-technical Hindi-speaking users
   Language: Hindi (Pre-translated, no runtime translation)
   
   Design Rules:
   - Simple vocabulary (सरल शब्दावली)
   - No probabilities shown directly (qualitative risk labels)
   - Clear next-step guidance
   - Pre-translated static text (no LLM)
   
   Updated: Feb 2026
   ============================================================================= #}
<!DOCTYPE html>
<html lang="hi">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>आपके फेफड़े की स्कैन रिपोर्ट</title>
  <style>
    /* Base Typography - Hindi Optimized */
    @font-face {
      font-family: "NotoDevanagari";
      src: url("file:///C:/Windows/Fonts/NotoSansDevanagari-Regular.ttf") format("truetype");
    }

    body {
      font-family: "NotoDevanagari", "Noto Sans Devanagari", "Mangal", Arial, sans-serif;
      color: #1f2937;
      font-size: 15px;
      line-height: 1.8;
      margin: 0;
      padding: 0;
      background: #fff;
    }

    .container {
      max-width: 700px;
      margin: 0 auto;
      padding: 24px;
    }

    /* Header */
    .header {
      text-align: center;
      padding: 20px 0;
      border-bottom: 3px solid #3b82f6;
      margin-bottom: 24px;
    }

    .header h1 {
      margin: 0;
      font-size: 26px;
      color: #1e3a5f;
    }

    .header .subtitle {
      color: #6b7280;
      font-size: 14px;
      margin-top: 6px;
    }

    .patient-info {
      background: #f0f9ff;
      padding: 12px 16px;
      border-radius: 8px;
      margin-top: 12px;
      font-size: 13px;
    }

    /* Section Cards */
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

    .card-title .icon {
      font-size: 20px;
    }

    /* Good/Neutral/Concern messaging */
    .message-good {
      background: #ecfdf5;
      border: 1px solid #10b981;
      border-radius: 8px;
      padding: 16px;
      color: #065f46;
      font-size: 15px;
    }

    .message-good::before {
      content: "✓ ";
      font-weight: bold;
    }

    .message-concern {
      background: #fef3c7;
      border: 1px solid #f59e0b;
      border-radius: 8px;
      padding: 16px;
      color: #92400e;
      font-size: 15px;
    }

    .message-concern::before {
      content: "⚠ ";
      font-weight: bold;
    }

    /* Findings Table */
    .findings-table {
      width: 100%;
      border-collapse: collapse;
      margin: 12px 0;
      font-size: 13px;
    }

    .findings-table th {
      text-align: left;
      padding: 10px 8px;
      background: #f8fafc;
      border-bottom: 2px solid #e2e8f0;
      color: #475569;
      font-weight: 600;
    }

    .findings-table td {
      padding: 12px 8px;
      border-bottom: 1px solid #f1f5f9;
    }

    /* Risk Labels (Hindi) */
    .risk-label {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 16px;
      font-weight: 600;
      font-size: 12px;
    }

    .risk-low {
      background: #d1fae5;
      color: #065f46;
    }

    .risk-moderate {
      background: #fef3c7;
      color: #92400e;
    }

    .risk-high {
      background: #fee2e2;
      color: #991b1b;
    }

    /* Next Steps Card */
    .next-steps {
      background: #eff6ff;
      border: 2px solid #3b82f6;
    }

    .next-steps .card-title {
      color: #1d4ed8;
    }

    .steps-list {
      margin: 0;
      padding-left: 20px;
    }

    .steps-list li {
      margin: 12px 0;
      color: #1e40af;
    }

    /* Footer */
    .footer {
      margin-top: 30px;
      padding: 16px;
      background: #f9fafb;
      border-radius: 8px;
      font-size: 12px;
      color: #6b7280;
      text-align: center;
    }

    /* Print */
    @media print {
      .container { max-width: 100%; }
      .card { break-inside: avoid; }
    }
  </style>
</head>
<body>
  <div class="container">

    <!-- शीर्षक (HEADER) -->
    <div class="header">
      <h1>🫁 आपके फेफड़े की स्कैन रिपोर्ट</h1>
      <div class="subtitle">आपकी छाती के सीटी स्कैन का सरल सारांश</div>
      <div class="patient-info">
        <strong>स्कैन आईडी:</strong> {{ study_uid or study_id or 'N/A' }} &nbsp;|&nbsp;
        <strong>तारीख:</strong> {{ scan_date or 'N/A' }}
      </div>
    </div>

    <!-- परिचय (OVERVIEW) -->
    <div class="card">
      <h2 class="card-title"><span class="icon">📋</span> यह रिपोर्ट क्या दिखाती है</h2>
      <p>
        यह रिपोर्ट आपकी हाल की छाती के सीटी स्कैन के परिणामों को सरल भाषा में समझाती है। 
        हमारी AI प्रणाली ने आपके फेफड़ों का विश्लेषण किया और महत्वपूर्ण जानकारी प्राप्त की 
        जो आपके डॉक्टर को आपके स्वास्थ्य को बेहतर समझने में मदद कर सकती है।
      </p>
    </div>

    <!-- मुख्य परिणाम (MAIN RESULT) -->
    <div class="card">
      <h2 class="card-title"><span class="icon">🔍</span> हमें क्या मिला</h2>
      
      {% set nodule_count = nodules|length if nodules else 0 %}
      {% set high_risk = high_risk_count or 0 %}
      
      {% if nodule_count == 0 %}
        <div class="message-good">
          आपके फेफड़ों में कोई चिंताजनक क्षेत्र (गांठ) नहीं मिला। 
          यह अच्छी खबर है! नियमित स्वास्थ्य जांच जारी रखें।
        </div>
      {% elif high_risk == 0 %}
        <div class="message-good">
          हमें आपके फेफड़ों में {{ nodule_count }} छोटे धब्बे मिले, लेकिन वे कम जोखिम वाले दिखते हैं। 
          आपके डॉक्टर निगरानी के लिए नियमित फॉलो-अप स्कैन सुझा सकते हैं।
        </div>
      {% else %}
        <div class="message-concern">
          हमें आपके फेफड़ों में {{ nodule_count }} धब्बे मिले। 
          इनमें से {{ high_risk }} पर आपके डॉक्टर का ध्यान देना जरूरी है।
          कृपया जल्द से जल्द यह रिपोर्ट अपने डॉक्टर को दिखाएं।
        </div>
      {% endif %}

      {% if nodules and nodule_count > 0 %}
      <h3 style="font-size: 15px; margin-top: 20px; color: #374151;">खोजों का विवरण</h3>
      <table class="findings-table">
        <thead>
          <tr>
            <th>धब्बा #</th>
            <th>आकार</th>
            <th>जोखिम स्तर</th>
            <th>इसका मतलब</th>
          </tr>
        </thead>
        <tbody>
          {% for n in nodules[:10] %}
          {% set prob = n.prob_malignant if n.prob_malignant is defined else (n.p_malignant if n.p_malignant is defined else 0) %}
          {% set risk_label = "उच्च" if prob >= 0.7 else ("मध्यम" if prob >= 0.4 else "कम") %}
          {% set risk_class = "high" if prob >= 0.7 else ("moderate" if prob >= 0.4 else "low") %}
          <tr>
            <td>#{{ n.id }}</td>
            <td>{{ n.long_axis_mm or 'छोटा' }} मिमी</td>
            <td>
              <span class="risk-label risk-{{ risk_class }}">{{ risk_label }}</span>
            </td>
            <td>
              {% if prob >= 0.7 %}
                आपके डॉक्टर को इसकी सावधानी से जांच करनी चाहिए।
              {% elif prob >= 0.4 %}
                फॉलो-अप स्कैन की आवश्यकता हो सकती है।
              {% else %}
                सामान्य दिखता है। नियमित जांच की सलाह है।
              {% endif %}
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
      
      {% if nodule_count > 10 %}
      <p style="font-size: 12px; color: #6b7280; margin-top: 8px;">
        {{ nodule_count }} धब्बों में से पहले 10 दिखाए जा रहे हैं। पूरी सूची आपके डॉक्टर के पास है।
      </p>
      {% endif %}
      {% endif %}
    </div>

    <!-- फेफड़ों का स्वास्थ्य (LUNG HEALTH) -->
    {% if lung_health %}
    <div class="card">
      <h2 class="card-title"><span class="icon">🫁</span> समग्र फेफड़ों का स्वास्थ्य</h2>
      <p>{{ lung_health }}</p>
    </div>
    {% endif %}

    <!-- आगे क्या करें (NEXT STEPS) -->
    <div class="card next-steps">
      <h2 class="card-title"><span class="icon">👉</span> आगे क्या करें</h2>
      
      {% if high_risk and high_risk > 0 %}
      <ol class="steps-list">
        <li><strong>यह रिपोर्ट जल्द से जल्द</strong> अपने डॉक्टर को दिखाएं।</li>
        <li><strong>घबराएं नहीं</strong> — कई धब्बे हानिरहित निकलते हैं।</li>
        <li><strong>अपने डॉक्टर से पूछें</strong> कि क्या आपको और टेस्ट या फॉलो-अप स्कैन की जरूरत है।</li>
        <li><strong>अपने सवाल लिख लें</strong> जो आप डॉक्टर से पूछना चाहते हैं।</li>
      </ol>
      {% else %}
      <ol class="steps-list">
        <li><strong>यह रिपोर्ट</strong> अपनी अगली मुलाकात में अपने डॉक्टर को दिखाएं।</li>
        <li><strong>नियमित जांच जारी रखें</strong> जैसा आपके डॉक्टर ने सलाह दी है।</li>
        <li><strong>स्वस्थ आदतें बनाए रखें</strong> — धूम्रपान से बचें और सक्रिय रहें।</li>
      </ol>
      {% endif %}
    </div>

    <!-- पाद लेख (FOOTER) -->
    <div class="footer">
      <p><strong>महत्वपूर्ण:</strong> यह रिपोर्ट केवल जानकारी के लिए है और आपके डॉक्टर की सलाह का विकल्प नहीं है।</p>
      <p>रिपोर्ट जनरेट: {{ generation_time or 'N/A' }} | हेल्थATM AI</p>
    </div>

  </div>
</body>
</html>
