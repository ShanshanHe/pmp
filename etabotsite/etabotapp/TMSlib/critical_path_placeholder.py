from email.mime.multipart import MIMEMultipart


def generate_critical_paths_email_report_for_tms(*, tms_wrapper, final_nodes, params):
    return MIMEMultipart('related')
