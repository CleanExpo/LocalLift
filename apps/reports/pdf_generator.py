"""
PDF Generator Module

This module provides the core PDF generation functionality for LocalLift reports.
It uses WeasyPrint to convert HTML templates to PDF files.
"""

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import os
import logging
from pathlib import Path

# Configure logger
logger = logging.getLogger(__name__)

# Constants
TEMPLATE_DIR = "templates/reports"
EXPORT_DIR = "exports"


def generate_pdf(template_file, context, output_filename, css_files=None):
    """
    Generate a PDF file from a Jinja2 template.
    
    Args:
        template_file (str): The name of the template file in the templates/reports directory
        context (dict): A dictionary of variables to pass to the template
        output_filename (str): The name of the output PDF file
        css_files (list): Optional list of CSS files to apply to the HTML
        
    Returns:
        str: The path to the generated PDF file
    """
    try:
        # Ensure the export directory exists
        os.makedirs(EXPORT_DIR, exist_ok=True)
        
        # Set up Jinja2 environment
        env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
        template = env.get_template(template_file)
        
        # Render template with context
        html_content = template.render(**context)
        
        # Create HTML object
        html = HTML(string=html_content)
        
        # Set output path
        output_path = os.path.join(EXPORT_DIR, output_filename)
        
        # Generate PDF
        if css_files:
            html.write_pdf(output_path, stylesheets=css_files)
        else:
            html.write_pdf(output_path)
        
        logger.info(f"PDF report generated: {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        raise


def get_report_url(filename):
    """
    Get the URL for a generated report.
    
    Args:
        filename (str): The filename of the report
        
    Returns:
        str: The URL path to access the report
    """
    return f"/exports/{filename}"


def list_reports(client_id=None):
    """
    List all generated reports, optionally filtered by client ID.
    
    Args:
        client_id (str, optional): Client ID to filter reports by
        
    Returns:
        list: List of report filenames
    """
    reports = []
    try:
        for file in os.listdir(EXPORT_DIR):
            if file.endswith(".pdf"):
                if client_id is None or file.startswith(f"{client_id}_"):
                    reports.append(file)
        return reports
    except Exception as e:
        logger.error(f"Error listing reports: {str(e)}")
        return []


def delete_report(filename):
    """
    Delete a report file.
    
    Args:
        filename (str): The filename of the report to delete
        
    Returns:
        bool: True if the file was deleted, False otherwise
    """
    try:
        os.remove(os.path.join(EXPORT_DIR, filename))
        logger.info(f"Report deleted: {filename}")
        return True
    except Exception as e:
        logger.error(f"Error deleting report: {str(e)}")
        return False


def cleanup_old_reports(days=30):
    """
    Clean up reports older than a specified number of days.
    
    Args:
        days (int): Age in days of reports to delete
        
    Returns:
        int: Number of files deleted
    """
    import time
    from datetime import datetime, timedelta
    
    cutoff_time = (datetime.now() - timedelta(days=days)).timestamp()
    deleted_count = 0
    
    try:
        for file in os.listdir(EXPORT_DIR):
            if file.endswith(".pdf"):
                file_path = os.path.join(EXPORT_DIR, file)
                if os.path.getmtime(file_path) < cutoff_time:
                    os.remove(file_path)
                    deleted_count += 1
                    logger.info(f"Deleted old report: {file}")
        
        return deleted_count
    except Exception as e:
        logger.error(f"Error cleaning up old reports: {str(e)}")
        return 0
