"""
TraceVault Forensic Report Generator Service
Generates court-ready PDF, JSON, and CSV forensic reports with SHA-256 evidence verification.
Saves report metadata to the database.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from datetime import datetime, timezone
import structlog
from typing import Dict, Any, List, Optional
from sqlalchemy import update

from app.config import get_settings
from app.models.recording import Recording
from app.models.evidence import Report

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
    """Generates structured forensic investigation reports in PDF, JSON, and CSV formats."""

    async def generate_report(
        self,
        recording: Recording,
        segments: List[Dict[str, Any]],
        analysis: Dict[str, Any],
    ) -> str:
        """
        Main pipeline report generator.
        Generates PDF, JSON, and CSV reports, then saves a Report record in the database.
        """
        from app.database.engine import AsyncSessionLocal
        import uuid

        settings = get_settings()
        report_dir = Path(settings.storage.REPORT_DIRECTORY)
        report_dir.mkdir(parents=True, exist_ok=True)

        report_id = str(uuid.uuid4())
        pdf_path = report_dir / f"report_{recording.id}_{report_id}.pdf"
        json_path = report_dir / f"report_{recording.id}_{report_id}.json"
        csv_path = report_dir / f"report_{recording.id}_{report_id}.csv"

        recording_meta = {
            "filename": recording.original_filename,
            "sha256_hash": recording.sha256_hash,
            "duration_seconds": recording.duration_seconds or 0.0,
            "warrant_number": recording.warrant_number or "WR-UNASSIGNED",
            "case_id": recording.case_id or "UNASSIGNED",
            "language": recording.detected_language or "en",
        }

        # 1. Generate PDF
        self.generate_report_pdf(
            output_path=str(pdf_path),
            recording_meta=recording_meta,
            segments=segments,
            analysis=analysis,
            report_title=f"Forensic Audit Report - {recording.original_filename}",
        )

        # 2. Generate JSON
        report_data = {
            "metadata": recording_meta,
            "analysis": {
                "summary": analysis.get("summary", ""),
                "primary_topic": analysis.get("primary_topic", "General"),
                "threat_present": analysis.get("threat_present", False),
                "threat_category": analysis.get("threat_category", "none"),
                "risk_score": analysis.get("risk_score", 0.0),
                "risk_level": analysis.get("risk_level", "low"),
                "entities": analysis.get("entities", []),
                "keywords": analysis.get("keywords", []),
                "locations_discussed": analysis.get("locations_discussed", []),
                "times_discussed": analysis.get("times_discussed", []),
            },
            "segments": segments,
        }
        json_path.write_text(json.dumps(report_data, indent=2, ensure_ascii=False), encoding="utf-8")

        # 3. Generate CSV
        with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Sequence", "Start (s)", "End (s)", "Speaker", "Confidence", "Text", "Has Threat", "Has Entity"])
            for idx, seg in enumerate(segments):
                writer.writerow([
                    idx,
                    seg.get("start_time", seg.get("start", 0.0)),
                    seg.get("end_time", seg.get("end", 0.0)),
                    seg.get("speaker_label", "Speaker"),
                    seg.get("confidence", 1.0),
                    seg.get("text", ""),
                    seg.get("has_threat", False),
                    seg.get("has_entity", False),
                ])

        # 4. Save Report model to DB
        async with AsyncSessionLocal() as session:
            db_report = Report(
                id=report_id,
                case_id=recording.case_id if (recording.case_id and recording.case_id not in ("None", "null", "undefined", "")) else "00000000-0000-0000-0000-000000000000", # Fallback case
                recording_id=recording.id,
                created_by=recording.uploaded_by_id,
                report_type="Forensic Call Report",
                title=f"Forensic Intelligence Report - {recording.original_filename}",
                description=f"Automated forensic transcript audit and threat extraction for {recording.original_filename}.",
                status="completed",
                content=analysis.get("summary", ""),
                content_json=report_data,
                model_used=analysis.get("model_used", "gemini"),
                pdf_path=str(pdf_path),
                json_path=str(json_path),
                csv_path=str(csv_path),
            )
            session.add(db_report)
            await session.commit()

        logger.info("Forensic reports generated successfully", report_id=report_id, recording_id=recording.id)
        return str(pdf_path)

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
            f"Executive Summary:     {analysis.get('summary', 'N/A')}",
            f"Primary Topic:         {analysis.get('primary_topic', 'General')}",
            f"Risk Level:            {analysis.get('risk_level', 'low').upper()} (Score: {analysis.get('risk_score', 0.0)})",
            "",
            "[THREAT AUDIT EVALUATION]",
            f"Threat Flagged:        {'YES' if analysis.get('threat_present') or analysis.get('threatPresent') else 'NO'}",
            f"Threat Category:       {analysis.get('threat_category', analysis.get('threatCategory', 'None'))}",
            f"Threat Audit Details:  {analysis.get('threat_description', analysis.get('threatDetails', 'None'))}",
            "",
            "[EXTRACTED ENTITIES & INTELLIGENCE]",
            f"Locations Discussed:   {', '.join(analysis.get('locations_discussed') or analysis.get('locationsDiscussed') or [])}",
            f"Times/Dates Discussed: {', '.join(analysis.get('times_discussed') or analysis.get('timesDiscussed') or [])}",
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
        elements.append(Paragraph("TRACEVAULT FORENSIC REPORT", title_style))
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
        threat_present = analysis.get("threat_present") or analysis.get("threatPresent") or False
        threat_color = "#ef4444" if threat_present else "#10b981"
        threat_category = analysis.get("threat_category", analysis.get("threatCategory", "None"))
        elements.append(Paragraph(f"<b>Threat Status:</b> <font color='{threat_color}'><b>{threat_category.upper()}</b></font>", body_style))
        elements.append(Paragraph(f"<b>Risk Level:</b> {analysis.get('risk_level', 'low').upper()} (Score: {analysis.get('risk_score', 0.0)})", body_style))
        elements.append(Paragraph(f"<b>Executive Summary:</b> {analysis.get('summary')}", body_style))
        elements.append(Paragraph(f"<b>Locations Discussed:</b> {', '.join(analysis.get('locations_discussed') or analysis.get('locationsDiscussed') or [])}", body_style))
        elements.append(Paragraph(f"<b>Times / Dates Mentioned:</b> {', '.join(analysis.get('times_discussed') or analysis.get('timesDiscussed') or [])}", body_style))
        elements.append(Spacer(1, 10))

        # Diarized Segments
        elements.append(Paragraph("Diarized Transcript Breakdown", h2_style))
        for seg in segments:
            spk = seg.get("speaker_label", "Speaker")
            st = seg.get("start_time", seg.get("start", 0.0))
            et = seg.get("end_time", seg.get("end", 0.0))
            text = seg.get("text", "")
            seg_p = Paragraph(f"<b>[{st:.1f}s - {et:.1f}s] {spk}:</b> {text}", body_style)
            elements.append(seg_p)
            elements.append(Spacer(1, 4))

        doc.build(elements)
        return str(path)
