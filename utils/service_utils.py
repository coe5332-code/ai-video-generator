# utils/service_utils.py
import os


def create_service_sections(service_content):
    """
    Create structured sections for BSK training video generation
    """
    sections = []

    # Introduction slide - Service overview for operators
    if service_content["service_name"] and service_content["service_description"]:
        intro_text = f"Welcome to BSK Training: {service_content['service_name']}. As a data entry operator at Bangla Sahayta Kendra, you will help citizens access this important service. {service_content['service_description']}"
        sections.append(
            ("Service Introduction", intro_text, "government service training")
        )

    # Eligibility Verification slide
    if service_content["eligibility_criteria"].strip():
        eligibility_text = f"Before helping citizens apply for {service_content['service_name']}, verify they meet these eligibility criteria: {service_content['eligibility_criteria']}"
        sections.append(
            ("Eligibility Verification", eligibility_text, "verification checklist")
        )

    # Document Checklist slide
    if service_content["required_docs"].strip():
        docs_text = f"Document checklist for {service_content['service_name']}. Help citizens prepare these documents: {service_content['required_docs']}"
        sections.append(("Document Verification", docs_text, "documents checklist"))

    # Step-by-Step Process slide
    if service_content["how_to_apply"].strip():
        process_text = f"Follow these steps to help citizens apply for {service_content['service_name']}: {service_content['how_to_apply']}"
        sections.append(("Application Process", process_text, "step by step process"))

    # Operator Tips slide
    if service_content.get("operator_tips", "").strip():
        tips_text = f"Professional tips for BSK operators handling {service_content['service_name']}: {service_content['operator_tips']}"
        sections.append(("Operator Guidelines", tips_text, "professional tips"))

    # Troubleshooting slide
    if service_content.get("troubleshooting", "").strip():
        troubleshoot_text = f"Common issues and solutions for {service_content['service_name']}: {service_content['troubleshooting']}"
        sections.append(("Troubleshooting Guide", troubleshoot_text, "problem solving"))

    # Fees and Timeline slide
    if service_content.get("fees_and_timeline", "").strip():
        fees_text = f"Inform citizens about fees and processing time for {service_content['service_name']}: {service_content['fees_and_timeline']}"
        sections.append(("Fees & Timeline", fees_text, "cost timeline"))

    # Service Link slide
    if service_content["service_link"].strip():
        link_text = f"Guide citizens to access {service_content['service_name']} online at: {service_content['service_link']}. Help them navigate the official website if needed."
        sections.append(("Online Access", link_text, "website online"))

    # Conclusion slide
    conclusion_text = f"Thank you for completing the {service_content['service_name']} training. You are now ready to help citizens with this service at Bangla Sahayta Kendra. Remember to be patient, helpful, and professional in all interactions."
    sections.append(("Training Complete", conclusion_text, "graduation success"))

    return sections


def validate_service_content(service_content):
    """
    Validate that minimum required fields are provided for BSK training
    """
    if not service_content["service_name"].strip():
        return False, "Service name is required"

    if not service_content["service_description"].strip():
        return False, "Service description is required"

    if not service_content["how_to_apply"].strip():
        return False, "Step-by-step application process is required"

    if not service_content["eligibility_criteria"].strip():
        return False, "Eligibility criteria is required"

    if not service_content["required_docs"].strip():
        return False, "Required documents checklist is required"

    return True, "Valid training content for BSK operators"


def create_training_sections(training_content):
    """
    Create structured sections for training video generation
    """
    sections = []

    # Introduction slide
    if training_content.get("training_name") and training_content.get(
        "training_description"
    ):
        intro_text = f"Welcome to {training_content['training_name']}. {training_content['training_description']}"
        sections.append(("Introduction", intro_text, "training education"))

    # Objectives slide
    if training_content.get("objectives", "").strip():
        objectives_text = f"Training objectives for {training_content['training_name']}: {training_content['objectives']}"
        sections.append(("Objectives", objectives_text, "goals objectives"))

    # Prerequisites slide
    if training_content.get("prerequisites", "").strip():
        prereq_text = f"Prerequisites for {training_content['training_name']}: {training_content['prerequisites']}"
        sections.append(("Prerequisites", prereq_text, "requirements prerequisites"))

    # Course Content slide
    if training_content.get("course_content", "").strip():
        content_text = f"Course content for {training_content['training_name']}: {training_content['course_content']}"
        sections.append(("Course Content", content_text, "curriculum learning"))

    # Certification slide
    if training_content.get("certification", "").strip():
        cert_text = f"Certification details for {training_content['training_name']}: {training_content['certification']}"
        sections.append(("Certification", cert_text, "certificate achievement"))

    return sections
