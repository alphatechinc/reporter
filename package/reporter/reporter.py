#!/usr/bin/python
import argparse
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import simplejson.scanner
from decimal import Decimal
import os
import logging
import reporter_config as conf

def get_report_html(yahoo_dict):
    report_html = '<html><table>'
    '''
    todo: build email contents
    '''
    report_html += '</table></html>'
    return report_html

def send_html_report_as_email(recipient_list, html):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = conf.subject
    msg['from'] = conf.sender
    msg['To'] = recipient_list
    msg.attach(MIMEText(html, 'html'))
    server = smtplib.SMTP('localhost')
    logging.debug('Emailing ' + str(conf.name) + ' to ' + str(recipient_list))
    server.sendmail(conf.email_from, recipient_list, msg.as_string())
    server.quit()

def get_script_path():
    return os.path.dirname(os.path.realpath(__file__))

def main(parser_args):
    """
    TODO: Implement recipient list
    """
    html = get_report_html()
    if parser_args.no_email:
        print html
    else:
        send_html_report_as_email(recipient_list, html)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Reporter')
    parser.add_argument('--debug', action='store_true', help='Increase verbosity to Logging.DEBUG. (default = logging.ERROR)')
    parser.add_argument('--no_email', action='store_true', help='Don\'t send an email.')
    parser_args = parser.parse_args()

    log_level = logging.DEBUG if parser_args.debug else logging.ERROR
    log_format = '%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        filename = os.path.dirname(os.path.realpath(__file__)) + '/reporter.log',
        level = log_level,
        format = log_format,
        )
    logging.captureWarnings(True)

    logging.debug('Starting Reporter.')

    if parser_args.debug:
        root = logging.getLogger()
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.getLogger().getEffectiveLevel())
        ch.setFormatter(logging.Formatter(log_format))
        root.addHandler(ch)

    main(parser_args)
    logging.debug('Completed Reporter.')