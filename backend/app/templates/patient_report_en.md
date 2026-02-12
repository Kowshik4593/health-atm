{# =============================================================================
   Patient Report Template - English (Phase-2)
   
   Purpose: Understandable by rural / non-technical users
   Language: English
   
   Design Rules:
   - Simple vocabulary
   - No probabilities shown directly (qualitative risk labels)
   - Clear next-step guidance
   - Simplified icons
   
   Updated: Feb 2026
   ============================================================================= #}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Your Lung Scan Results</title>
  <style>
    /* Base Typography */
    body {
      font-family: "Segoe UI", "Noto Sans", Arial, sans-serif;
      color: #1f2937;
      font-size: 14px;
      line-height: 1.6;
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
      font-size: 24px;
      color: #1e3a5f;
    }

    .header .subtitle {
      color: #6b7280;
      font-size: 14px;
      margin-top: 4px;
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

    /* Findings Table (Simple) */
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

    /* Risk Labels (Patient-Friendly) */
    .risk-label {
      display: inline-block;
      padding: 4px 12px;
      border-radius: 16px;
      font-weight: 600;
      font-size: 12px;
      text-transform: uppercase;
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

    /* Guidance Text */
    .guidance {
      font-size: 13px;
      color: #6b7280;
      margin-top: 8px;
      padding-left: 12px;
      border-left: 3px solid #e5e7eb;
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
      margin: 10px 0;
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

    .footer strong {
      color: #374151;
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

    <!-- HEADER -->
    <div class="header">
      <h1>🫁 Your Lung Scan Results</h1>
      <div class="subtitle">Easy-to-understand summary of your chest CT scan</div>
      <div class="patient-info">
        <strong>Scan ID:</strong> {{ study_uid or study_id or 'N/A' }} &nbsp;|&nbsp;
        <strong>Date:</strong> {{ scan_date or 'N/A' }}
      </div>
    </div>

    <!-- OVERVIEW -->
    <div class="card">
      <h2 class="card-title"><span class="icon">📋</span> What This Report Shows</h2>
      <p>
        This report explains the results of your recent chest CT scan in simple terms. 
        Our AI system analyzed your lungs and found important details that can help your doctor 
        understand your health better.
      </p>
    </div>

    <!-- MAIN RESULT -->
    <div class="card">
      <h2 class="card-title"><span class="icon">🔍</span> What We Found</h2>
      
      {% set nodule_count = nodules|length if nodules else 0 %}
      {% set high_risk = high_risk_count or 0 %}
      
      {% if nodule_count == 0 %}
        <div class="message-good">
          No concerning areas (nodules) were found in your lungs. 
          This is good news! Continue with regular health checkups.
        </div>
      {% elif high_risk == 0 %}
        <div class="message-good">
          We found {{ nodule_count }} small spot(s) in your lungs, but they appear to be low risk. 
          Your doctor may suggest routine follow-up scans to monitor them.
        </div>
      {% else %}
        <div class="message-concern">
          We found {{ nodule_count }} spot(s) in your lungs. 
          {{ high_risk }} of them need attention from your doctor.
          Please share this report with your doctor soon.
        </div>
      {% endif %}

      {% if nodules and nodule_count > 0 %}
      <h3 style="font-size: 15px; margin-top: 20px; color: #374151;">Details of Findings</h3>
      <table class="findings-table">
        <thead>
          <tr>
            <th>Spot #</th>
            <th>Size</th>
            <th>Risk Level</th>
            <th>What This Means</th>
          </tr>
        </thead>
        <tbody>
          {% for n in nodules[:10] %}
          {% set prob = n.prob_malignant if n.prob_malignant is defined else (n.p_malignant if n.p_malignant is defined else 0) %}
          {% set risk_label = "High" if prob >= 0.7 else ("Moderate" if prob >= 0.4 else "Low") %}
          <tr>
            <td>#{{ n.id }}</td>
            <td>{{ n.long_axis_mm or 'Small' }} mm</td>
            <td>
              <span class="risk-label risk-{{ risk_label|lower }}">{{ risk_label }}</span>
            </td>
            <td>
              {% if risk_label == "High" %}
                Your doctor should review this carefully.
              {% elif risk_label == "Moderate" %}
                May need a follow-up scan.
              {% else %}
                Looks normal. Regular checkups advised.
              {% endif %}
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
      
      {% if nodule_count > 10 %}
      <p style="font-size: 12px; color: #6b7280; margin-top: 8px;">
        Showing first 10 of {{ nodule_count }} spots. Your doctor has the full list.
      </p>
      {% endif %}
      {% endif %}
    </div>

    <!-- LUNG HEALTH SUMMARY -->
    {% if lung_health %}
    <div class="card">
      <h2 class="card-title"><span class="icon">🫁</span> Overall Lung Health</h2>
      <p>{{ lung_health }}</p>
    </div>
    {% endif %}

    <!-- NEXT STEPS -->
    <div class="card next-steps">
      <h2 class="card-title"><span class="icon">👉</span> What To Do Next</h2>
      
      {% if high_risk and high_risk > 0 %}
      <ol class="steps-list">
        <li><strong>Share this report</strong> with your doctor as soon as possible.</li>
        <li><strong>Don't panic</strong> — many spots turn out to be harmless.</li>
        <li><strong>Ask your doctor</strong> if you need more tests or a follow-up scan.</li>
        <li><strong>Write down questions</strong> you want to ask your doctor.</li>
      </ol>
      {% else %}
      <ol class="steps-list">
        <li><strong>Share this report</strong> with your doctor at your next visit.</li>
        <li><strong>Continue regular checkups</strong> as advised by your doctor.</li>
        <li><strong>Maintain healthy habits</strong> — avoid smoking and stay active.</li>
      </ol>
      {% endif %}
    </div>

    <!-- XAI VISUAL EXPLANATION (For High-Risk Findings) -->
    {% if xai_gallery %}
    <div class="card">
      <h2 class="card-title"><span class="icon">🔬</span> How AI Analyzed Your Scan</h2>
      <p style="font-size: 13px; color: #6b7280; margin-bottom: 12px;">
        These images show where the AI focused when looking at your scan. 
        The colored areas highlight regions the AI examined more closely.
        Your doctor will use these to better understand the findings.
      </p>
      {{ xai_gallery|safe }}
    </div>
    {% endif %}

    <!-- FOOTER -->
    <div class="footer">
      <p><strong>Important:</strong> This report is for information only and does not replace advice from your doctor.</p>
      <p>Report generated: {{ generation_time or 'N/A' }} | HealthATM AI</p>
    </div>

  </div>
</body>
</html>
