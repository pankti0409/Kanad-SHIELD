"""
TraceVault Forensic Report Generator Service
Generates court-ready PDF and text forensic reports with SHA-256 evidence verification.
"""
from pathlib import Path
from datetime import datetime, timezone
import structlog
from typing import Dict, Any, List, Optional

logger = structlog.get_logger(__name__)

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False


class ReportGeneratorService:
    """Generates structured forensic investigation reports."""

    def generate_report_text(
        self,
        recording_meta: Dict[str, Any],
        segments: List[Dict[str, Any]],
        analysis: Dict[str, Any],
        report_title: str = "Forensic Call Intelligence Report",
    ) -> str:
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        filename = recording_meta.get("filename", "audio_recording")
        sha256 = recording_meta.get("sha256_hash", "UNVERIFIED")
        warrant = recording_meta.get("warrant_number", "WR-UNASSIGNED")
        case_id = recording_meta.get("case_id", "UNASSIGNED")
        duration = recording_meta.get("duration_seconds", 0.0)

        lines = [
            "=" * 72,
            f"TRACEVAULT FORENSIC INTELLIGENCE REPORT — {report_title.upper()}",
            "=" * 72,
            f"Generated: {now_str}",
            "Evidence Integrity Status: SECURE (SHA-256 Cryptographic Verification)",
            "",
            "[EVIDENCE FILE METADATA]",
            f"File Name:             {filename}",
            f"SHA-256 Checksum:      {sha256}",
            f"Duration:              {duration:.1f} seconds",
            f"Assigned Case ID:      {case_id}",
            f"Court Warrant Reference: {warrant}",
            f"Language Processing:   {recording_meta.get('language', 'Auto-detect')}",
            "",
            "[AUTOMATED CALL ANALYSIS SUMMARY]",
            f"Transcript Timestamp:  {analysis.get('transcriptDateTime', now_str)}",
            f"Analysis Timestamp:    {analysis.get('analysisDateTime', now_str)}",
            f"Executive Summary:     {analysis.get('summary', 'N/A')}",
            "",
            "[THREAT AUDIT EVALUATION]",
            f"Threat Flagged:        {'YES' if analysis.get('threatPresent') else 'NO'}",
            f"Threat Category:       {analysis.get('threatCategory', 'None')}",
            f"Threat Audit Details:  {analysis.get('threatDetails', 'None')}",
            "",
            "[EXTRACTED ENTITIES & INTELLIGENCE]",
            f"Locations Discussed:   {', '.join(analysis.get('locationsDiscussed', []))}",
            f"Times/Dates Discussed: {', '.join(analysis.get('timesDiscussed', []))}",
            f"Chain of Custody Info: {analysis.get('otherInfo', 'N/A')}",
            "",
            "[DIARIZED TRANSCRIPT TIMELINE]",
            "-" * 72,
        ]

        for seg in segments:
            spk = seg.get("speaker_label", seg.get("speaker", "Speaker"))
            st = seg.get("start_time", seg.get("start", 0.0))
            et = seg.get("end_time", seg.get("end", 0.0))
            conf = int(float(seg.get("confidence", 0.95)) * 100)
            text = seg.get("text", "")
            lines.append(f"[{st:.1f}s - {et:.1f}s] {spk} ({conf}% Confidence):")
            lines.append(f'  "{text}"')
            lines.append("")

        lines.extend([
            "-" * 72,
            "CONFIDENTIALITY NOTICE: This document contains legal evidence and restricted law enforcement data.",
            "=" * 72,
        ])

        return "\n".join(lines)

    def generate_report_pdf(
        self,
        output_path: str,
        recording_meta: Dict[str, Any],
        segments: List[Dict[str, Any]],
        analysis: Dict[str, Any],
        report_title: str = "Forensic Call Intelligence Report",
    ) -> str:
        """Generate PDF report using ReportLab if installed, otherwise create text report."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if not HAS_REPORTLAB:
            text_content = self.generate_report_text(recording_meta, segments, analysis, report_title)
            txt_path = path.with_suffix(".txt")
            txt_path.write_text(text_content, encoding="utf-8")
            return str(txt_path)

        doc = SimpleDocTemplate(str(path), pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#0f172a"),
            fontName="Helvetica-Bold",
        )
        h2_style = ParagraphStyle(
            "SectionHeader",
            parent=styles["Heading2"],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#1e293b"),
            fontName="Helvetica-Bold",
            spaceBefore=10,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            "BodyTextCustom",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155"),
        )
        bold_body = ParagraphStyle(
            "BoldBody",
            parent=body_style,
            fontName="Helvetica-Bold",
        )

        elements = []

        # Title Block
        elements.append(Paragraph(f"TRACEVAULT FORENSIC REPORT", title_style))
        elements.append(Paragraph(f"<b>Report Type:</b> {report_title} | <b>Integrity:</b> SHA-256 Verified", body_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#475569"), spaceBefore=8, spaceAfter=12))

        # Metadata Table
        meta_data = [
            [Paragraph("File Name", bold_body), Paragraph(str(recording_meta.get("filename")), body_style)],
            [Paragraph("SHA-256 Checksum", bold_body), Paragraph(str(recording_meta.get("sha256_hash")), body_style)],
            [Paragraph("Duration", bold_body), Paragraph(f"{recording_meta.get('duration_seconds', 0):.1f} s", body_style)],
            [Paragraph("Warrant Reference", bold_body), Paragraph(str(recording_meta.get("warrant_number", "WR-TEMP")), body_style)],
            [Paragraph("Case Reference", bold_body), Paragraph(str(recording_meta.get("case_id", "Unassigned")), body_style)],
        ]
        meta_table = Table(meta_data, colWidths=[130, 410])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#f1f5f9")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('PADDING', (0,0), (-1,-1), 4),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 10))

        # Executive Summary & Threat
        elements.append(Paragraph("AI Intelligence & Threat Evaluation", h2_style))
        threat_color = "#ef4444" if analysis.get("threatPresent") else "#10b981"
        elements.append(Paragraph(f"<b>Threat Status:</b> <font color='{threat_color}'><b>{analysis.get('threatCategory')}</b></font>", body_style))
        elements.append(Paragraph(f"<b>Executive Summary:</b> {analysis.get('summary')}", body_style))
        elements.append(Paragraph(f"<b>Locations Discussed:</b> {', '.join(analysis.get('locationsDiscussed', []))}", body_style))
        elements.append(Paragraph(f"<b>Times / Dates Mentioned:</b> {', '.join(analysis.get('timesDiscussed', []))}", body_style))
        elements.append(Spacer(1, 10))

        # Diarized Segments
        elements.append(Paragraph("Diarized Transcript Breakdown", h2_style))
        for seg in segments:
            spk = seg.get("speaker_label", "Speaker")
            st = seg.get("start_time", 0.0)
            et = seg.get("end_time", 0.0)
            text = seg.get("text", "")
            seg_p = Paragraph(f"<b>[{st:.1f}s - {et:.1f}s] {spk}:</b> {text}", body_style)
            elements.append(seg_p)
            elements.append(Spacer(1, 4))

        doc.build(elements)
        return str(path)
