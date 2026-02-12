{# patient_summary_sectioned.md - sectioned English template #}

<!-- SECTION:OVERVIEW -->
This report summarizes the findings from your recent chest CT scan.  
Our AI system analyzed your lungs and identified important details that can help your doctor understand your condition.
<!-- END:OVERVIEW -->


<!-- SECTION:LUNG_CONDITION -->
Overall Lung Status: {{ lung_health or "Not Available" }}

{% if airway_wall_thickness %}
Airway Wall Condition: {{ airway_wall_thickness }}
{% endif %}

{% if emphysema_score is not none %}
Emphysema Score: {{ emphysema_score }}
{% endif %}

{% if fibrosis_score is not none %}
Fibrosis Score: {{ fibrosis_score }}
{% endif %}

{% if consolidation_score is not none %}
Consolidation Score: {{ consolidation_score }}
{% endif %}
<!-- END:LUNG_CONDITION -->


<!-- SECTION:NODULE_SUMMARY -->
Total Lung Nodules Found: {{ nodules | length }}
High-Risk Nodules (>70% chance): {{ high_risk_count }}

{% if nodules | length == 0 %}
No nodules were detected in this scan.

{% else %}
Detailed information on detected nodules:

{% for n in nodules %}
Nodule {{ loop.index }}
- Size (long axis): {{ n.long_axis_mm }} mm
- Volume: {{ n.volume_mm3 }} mm³
- Location: {{ n.location or "Not Available" }}
- Type: {{ n.type or "Not Available" }}
- Chance of being cancerous: {{ (n.prob_malignant * 100) | round(1) }}%
- Needs Review: {{ "Yes" if n.uncertainty.needs_review else "No" }}

{% endfor %}
{% endif %}
<!-- END:NODULE_SUMMARY -->


<!-- SECTION:IMPRESSION -->
{{ impression or "No impression was provided in the scan analysis." }}
<!-- END:IMPRESSION -->


<!-- SECTION:PATIENT_FRIENDLY_SUMMARY -->
{{ summary_text or "Your scan has been analyzed. Your doctor will review these findings and guide the next steps." }}
<!-- END:PATIENT_FRIENDLY_SUMMARY -->


<!-- SECTION:FOLLOW_UP -->
{% if high_risk_count > 0 %}
Some nodules require medical follow-up. Your doctor may recommend:
- Additional imaging tests  
- Short-term follow-up CT scan  
- Specialist consultation  

{% else %}
No high-risk nodules were detected. Routine monitoring may be sufficient.
{% endif %}
<!-- END:FOLLOW_UP -->
