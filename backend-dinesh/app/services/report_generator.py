# app/services/report_generator.py

import os
import json
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
from app.services.scan_result_service import ScanResultService


TEMPLATE_DIR = "app/templates"
OUTPUT_BASE = "app/local_reports"


class ReportGenerator:

    @staticmethod
    def generate_reports(case_id: str, findings_json_path: str):
        """
        Generates:
        - clinician_report.pdf
        - patient_report.pdf
        
        Stores them in:
            app/local_reports/<case_id>/

        Updates scan_results table with PDF filenames.
        """

        # ----------------------------------------------------------------------
        # LOAD FINDINGS JSON
        # ----------------------------------------------------------------------
        if not os.path.exists(findings_json_path):
            raise FileNotFoundError(f"Findings JSON not found at: {findings_json_path}")

        with open(findings_json_path, "r") as f:
            findings = json.load(f)

        # ----------------------------------------------------------------------
        # PREPARE OUTPUT DIRECTORY
        # ----------------------------------------------------------------------
        out_dir = os.path.join(OUTPUT_BASE, case_id)
        os.makedirs(out_dir, exist_ok=True)

        clinician_pdf_path = os.path.join(out_dir, "clinician_report.pdf")
        patient_pdf_path = os.path.join(out_dir, "patient_report.pdf")

        # ----------------------------------------------------------------------
        # LOAD TEMPLATES
        # ----------------------------------------------------------------------
        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))

        clinician_template = env.get_template("clinician_report.html")
        patient_template = env.get_template("patient_report.html")

        # ----------------------------------------------------------------------
        # RENDER HTML
        # ----------------------------------------------------------------------
        clinician_html = clinician_template.render(findings=findings, case_id=case_id)
        patient_html = patient_template.render(findings=findings, case_id=case_id)

        # ----------------------------------------------------------------------
        # GENERATE PDF FILES
        # ----------------------------------------------------------------------
        HTML(string=clinician_html).write_pdf(clinician_pdf_path)
        HTML(string=patient_html).write_pdf(patient_pdf_path)

        # ----------------------------------------------------------------------
        # UPDATE DB
        # Only store relative filenames — backend will convert to URLs
        # ----------------------------------------------------------------------
        ScanResultService.update_reports(
            scan_id=case_id,
            patient_pdf="patient_report.pdf",
            clinician_pdf="clinician_report.pdf",
        )

        return {
            "clinician_pdf": clinician_pdf_path,
            "patient_pdf": patient_pdf_path,
        }
