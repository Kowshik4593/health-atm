{# =============================================================================
   Clinician Report Template (Phase-2 Upgrade)
   
   Purpose: Decision support for radiologists / physicians
   Language: English only
   
   Features:
   - Tabular nodule summary with XAI references
   - High-risk nodule highlighting
   - Uncertainty flags
   - Validation warnings section
   - AI-assisted screening disclaimer
   
   Updated: Feb 2026
   ============================================================================= #}
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Clinician Report - {{ study_uid or study_id or 'Unknown' }}</title>
  <style>
    /* Base Typography */
    body {
      font-family: "Segoe UI", "Noto Sans", Arial, Helvetica, sans-serif;
      color: #1a1a2e;
      font-size: 12px;
      line-height: 1.5;
      margin: 0;
      padding: 0;
      background: #fff;
    }

    .container {
      max-width: 800px;
      margin: 0 auto;
      padding: 20px;
    }

    /* Header */
    .header-block {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      padding: 16px 0;
      border-bottom: 3px solid #1f3a5f;
      margin-bottom: 20px;
    }

    .brand-section h1 {
      margin: 0;
      font-size: 20px;
      color: #1f3a5f;
      font-weight: 700;
    }

    .brand-section .subtitle {
      font-size: 11px;
      color: #5c6b7a;
      margin-top: 2px;
    }

    .meta-section {
      text-align: right;
      font-size: 11px;
      color: #5c6b7a;
    }

    .meta-section .study-id {
      font-weight: 600;
      color: #1f3a5f;
      font-size: 12px;
    }

    /* Section Styling */
    .section {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      padding: 14px 16px;
      margin: 16px 0;
    }

    .section-title {
      margin: 0 0 10px 0;
      font-size: 13px;
      color: #1f3a5f;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      border-bottom: 1px solid #e2e8f0;
      padding-bottom: 6px;
    }

    /* Key-Value Grid */
    .kv-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px 24px;
    }

    .kv-item {
      display: flex;
      gap: 8px;
    }

    .kv-label {
      font-weight: 600;
      color: #475569;
      min-width: 140px;
    }

    .kv-value {
      color: #1a1a2e;
    }

    /* Nodule Table */
    .nodule-table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 10px;
      font-size: 11px;
    }

    .nodule-table th {
      text-align: left;
      padding: 8px 6px;
      background: #1f3a5f;
      color: #fff;
      font-weight: 600;
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.3px;
    }

    .nodule-table td {
      padding: 8px 6px;
      border-bottom: 1px solid #e2e8f0;
      vertical-align: middle;
    }

    .nodule-table tbody tr:hover {
      background: #f1f5f9;
    }

    .nodule-table tbody tr.high-risk {
      background: #fef2f2;
    }

    .nodule-table tbody tr.high-risk:hover {
      background: #fee2e2;
    }

    /* Risk Indicators */
    .risk-badge {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 12px;
      font-weight: 600;
      font-size: 10px;
      text-transform: uppercase;
    }

    .risk-high {
      background: #dc2626;
      color: #fff;
    }

    .risk-moderate {
      background: #f59e0b;
      color: #fff;
    }

    .risk-low {
      background: #10b981;
      color: #fff;
    }

    /* Review Flag */
    .review-flag {
      color: #dc2626;
      font-weight: 700;
    }

    .review-ok {
      color: #6b7280;
    }

    /* XAI Links */
    .xai-link {
      color: #2563eb;
      text-decoration: none;
      font-size: 10px;
    }

    .xai-link:hover {
      text-decoration: underline;
    }

    .xai-na {
      color: #9ca3af;
    }

    /* Warnings Section */
    .warnings-section {
      background: #fffbeb;
      border: 1px solid #fbbf24;
      border-left: 4px solid #f59e0b;
    }

    .warnings-section .section-title {
      color: #92400e;
      border-bottom-color: #fcd34d;
    }

    .warnings-list {
      margin: 0;
      padding-left: 20px;
    }

    .warnings-list li {
      margin: 4px 0;
      color: #92400e;
      font-size: 11px;
    }

    /* Impression Section */
    .impression-section {
      background: #f0f9ff;
      border-left: 4px solid #0ea5e9;
    }

    .impression-text {
      font-size: 12px;
      line-height: 1.6;
      color: #0c4a6e;
      white-space: pre-wrap;
    }

    /* Disclaimer */
    .disclaimer {
      background: #fef3c7;
      border: 1px solid #fcd34d;
      border-radius: 4px;
      padding: 10px 14px;
      margin-top: 20px;
      font-size: 11px;
    }

    .disclaimer strong {
      color: #92400e;
    }

    /* Footer */
    .footer {
      margin-top: 24px;
      padding-top: 12px;
      border-top: 1px solid #e2e8f0;
      font-size: 10px;
      color: #6b7280;
      display: flex;
      justify-content: space-between;
    }

    /* Print Styles */
    @media print {
      body { font-size: 10px; }
      .container { max-width: 100%; padding: 10px; }
      .section { break-inside: avoid; }
    }
  </style>
</head>
<body>
  <div class="container">

    <!-- HEADER -->
    <div class="header-block">
      <div class="brand-section">
        <h1>AI-Assisted Lung CT Analysis</h1>
        <div class="subtitle">Clinician Decision Support Report</div>
      </div>
      <div class="meta-section">
        <div class="study-id">{{ study_uid or study_id or 'N/A' }}</div>
        <div>Scan Date: {{ scan_date or 'N/A' }}</div>
        <div>Patient: {{ patient_name or 'N/A' }} ({{ patient_sex or 'N/A' }}, {{ patient_age or 'N/A' }} yrs)</div>
      </div>
    </div>

    <!-- VALIDATION WARNINGS (if any) -->
    {% if validation_warnings and validation_warnings|length > 0 %}
    <div class="section warnings-section">
      <h3 class="section-title">⚠️ Data Quality Warnings</h3>
      <ul class="warnings-list">
        {% for warning in validation_warnings[:10] %}
        <li>{{ warning }}</li>
        {% endfor %}
        {% if validation_warnings|length > 10 %}
        <li><em>... and {{ validation_warnings|length - 10 }} more warnings</em></li>
        {% endif %}
      </ul>
    </div>
    {% endif %}

    <!-- LUNG CONDITION SUMMARY -->
    <div class="section">
      <h3 class="section-title">Lung Condition Summary</h3>
      <div class="kv-grid">
        <div class="kv-item">
          <span class="kv-label">Overall Status:</span>
          <span class="kv-value">{{ lung_health or "Not assessed" }}</span>
        </div>
        <div class="kv-item">
          <span class="kv-label">Emphysema Score:</span>
          <span class="kv-value">{% if emphysema_score is not none %}{{ "%.4f"|format(emphysema_score) }}{% else %}N/A{% endif %}</span>
        </div>
        <div class="kv-item">
          <span class="kv-label">Fibrosis Score:</span>
          <span class="kv-value">{% if fibrosis_score is not none %}{{ "%.4f"|format(fibrosis_score) }}{% else %}N/A{% endif %}</span>
        </div>
        <div class="kv-item">
          <span class="kv-label">Consolidation Score:</span>
          <span class="kv-value">{% if consolidation_score is not none %}{{ "%.4f"|format(consolidation_score) }}{% else %}N/A{% endif %}</span>
        </div>
        <div class="kv-item">
          <span class="kv-label">Airway Wall:</span>
          <span class="kv-value">{{ airway_wall_thickness or "N/A" }}</span>
        </div>
        <div class="kv-item">
          <span class="kv-label">Processing Time:</span>
          <span class="kv-value">{% if processing_time_seconds %}{{ "%.2f"|format(processing_time_seconds) }} sec{% else %}N/A{% endif %}</span>
        </div>
      </div>
    </div>

    <!-- NODULE TABLE -->
    <div class="section">
      <h3 class="section-title">Detected Pulmonary Nodules ({{ nodules|length if nodules else 0 }})</h3>
      
      {% if nodules and nodules|length > 0 %}
      <table class="nodule-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Size (mm)</th>
            <th>Volume (mm³)</th>
            <th>Type</th>
            <th>Location</th>
            <th>Malignancy</th>
            <th>Review</th>
            <th>XAI</th>
          </tr>
        </thead>
        <tbody>
          {% for n in nodules %}
          {% set prob = n.prob_malignant if n.prob_malignant is defined else (n.p_malignant if n.p_malignant is defined else 0) %}
          {% set is_high_risk = prob >= 0.7 %}
          <tr class="{% if is_high_risk %}high-risk{% endif %}">
            <td>{{ n.id }}</td>
            <td>{{ n.long_axis_mm or 'N/A' }}</td>
            <td>{{ n.volume_mm3 or 'N/A' }}</td>
            <td>{{ n.type or 'unknown' }}</td>
            <td>{{ n.location or n.lobe or 'N/A' }}</td>
            <td>
              {% if prob >= 0.7 %}
                <span class="risk-badge risk-high">{{ (prob * 100)|round(1) }}%</span>
              {% elif prob >= 0.4 %}
                <span class="risk-badge risk-moderate">{{ (prob * 100)|round(1) }}%</span>
              {% else %}
                <span class="risk-badge risk-low">{{ (prob * 100)|round(1) }}%</span>
              {% endif %}
            </td>
            <td>
              {% set needs_review = n.uncertainty.needs_review if n.uncertainty is mapping else false %}
              {% if needs_review %}
                <span class="review-flag">Yes</span>
              {% else %}
                <span class="review-ok">No</span>
              {% endif %}
            </td>
            <td style="text-align:center;">
              {% if n.xai_embedded %}
                {{ n.xai_embedded|safe }}
              {% elif n.xai_html %}
                {{ n.xai_html|safe }}
              {% elif n.gradcam_path and n.gradcam_path != 'not_available' %}
                <a href="{{ n.gradcam_path }}" class="xai-link">CAM</a>
              {% elif n.overlay_path and n.overlay_path != 'not_available' %}
                <a href="{{ n.overlay_path }}" class="xai-link">Overlay</a>
              {% else %}
                <span class="xai-na">—</span>
              {% endif %}
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>

      {% if high_risk_count and high_risk_count > 0 %}
      <div style="margin-top: 10px; padding: 8px; background: #fef2f2; border-radius: 4px; font-size: 11px;">
        <strong style="color: #dc2626;">⚠️ {{ high_risk_count }} high-risk nodule(s) detected</strong> — 
        Clinical correlation and follow-up recommended.
      </div>
      {% endif %}

      {% else %}
      <p style="color: #6b7280; font-style: italic;">No nodules detected in this scan.</p>
      {% endif %}
    </div>

    <!-- IMPRESSION -->
    <div class="section impression-section">
      <h3 class="section-title">Clinical Impression</h3>
      <div class="impression-text">{{ impression or "No clinical impression generated. Recommend radiologist review." }}</div>
    </div>

    <!-- XAI SUMMARY -->
    {% if xai_summary %}
    <div class="section">
      <h3 class="section-title">Explainability Summary</h3>
      <p style="font-size: 11px; color: #475569;">{{ xai_summary.text }}</p>
      <p style="font-size: 10px; color: #6b7280; margin-top: 8px;">
        Visualizations available for {{ xai_summary.statistics.with_xai }}/{{ xai_summary.statistics.total_nodules }} nodules.
        {% if xai_summary.statistics.high_risk_without_xai > 0 %}
        <strong style="color: #dc2626;">{{ xai_summary.statistics.high_risk_without_xai }} high-risk nodule(s) lack XAI.</strong>
        {% endif %}
      </p>
    </div>
    {% endif %}

    <!-- XAI VISUAL GALLERY (Embedded Images) -->
    {% if xai_gallery %}
    {{ xai_gallery|safe }}
    {% endif %}

    <!-- DISCLAIMER -->
    <div class="disclaimer">
      <strong>⚕️ AI-Assisted Screening Notice:</strong> 
      This report was generated by automated AI analysis and is intended for decision support only. 
      All findings must be validated by a qualified radiologist or physician. 
      AI predictions are probabilistic and should not be used as the sole basis for clinical decisions.
    </div>

    <!-- FOOTER -->
    <div class="footer">
      <div>Generated: {{ generation_time or 'N/A' }}</div>
      <div>HealthATM AI v2.0 | Phase-2 Compliant</div>
    </div>

  </div>
</body>
</html>
