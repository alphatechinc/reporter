import logging
import os
import argparse
import yaml
import pymysql
from pymysql.cursors import DictCursorMixin, Cursor
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from collections import OrderedDict
from inflection import titleize
import locale

class OrderedDictCursor(DictCursorMixin, Cursor):
    dict_type = OrderedDict

def read_file_to_string(path):
    with open(path, 'r') as f:
        return f.read()

def mysql_query(sql, secrets):
    con = pymysql.connect(
        host=secrets['db-hostname'],
        port=secrets['db-port'],
        user=secrets['db-username'],
        password=secrets['db-password'],
        charset='utf8mb4',
        db=secrets['db-schema'],
        cursorclass=pymysql.cursors.DictCursor
        )

    with con.cursor(OrderedDictCursor) as cur:
        cur.execute(sql)
        results = cur.fetchall()

    con.close()

    return results

def prettify_column(val, column):
    base = column.split('__')[-1]
    funcs = {
        'dollars_cents': lambda v: locale.currency(int(v), grouping=True),
        'name': lambda v: titleize(v),
        'city_state': lambda v: ','.join([titleize(v.split(',')[0]), v.split(',')[1]]),
        }
    func = funcs.get(base, str)
    return func(val)

def html_from_sql_result(result_list):
    html = ''
    if len(result_list) > 0:
        html += '<table>'
        for row_num, row in enumerate(result_list):
	    if row_num == 0:
		html += '\n    <tr>'
		for k, v in row.iteritems():
		    html += '<th>' + titleize(str(k)) + '</th>'
		html += '\n    </tr>'

            html += '\n    <tr>'
            for k, v in row.iteritems():
		html += '<td>' + prettify_column(v, k) + '</td>'
            html += '</tr>'
        html += '\n</table>'
    else:
        html = 'Query returned no results.'

    return html

def send_html_report_as_email(subject, recipient_list, emails_from, html):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['from'] = emails_from
    msg['To'] = ','.join(recipient_list)
    msg.attach(MIMEText(html, 'html'))
    server = smtplib.SMTP('localhost')
    server.sendmail(emails_from, recipient_list, msg.as_string())
    server.quit()

def read_yaml_conf(fn):
    with open(fn, 'r') as f:
        yaml_dict = yaml.load(f)

    return yaml_dict

def main(parser_args):
    report_path = (parser_args.report_path or 'daily_report.yaml')
    secrets_path = (parser_args.secrets_path or 'secrets.yaml')

    secrets = read_yaml_conf(secrets_path)
    report_conf = read_yaml_conf(report_path)

    sql = read_file_to_string(report_conf['query-file'])

    res = mysql_query(sql, secrets)
    html = html_from_sql_result(res)

    if parser_args.no_email:
        print html
    else:
        send_html_report_as_email(report_conf['report-name'], report_conf['recipients'], report_conf['email-from'], html)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Reporter')
    parser.add_argument('report_path', type=str,  help='Path of the report.yaml file.')
    parser.add_argument('--debug', action='store_true', help='Increase verbosity to Logging.DEBUG. (default = logging.ERROR)')
    parser.add_argument('--no_email', action='store_true', help='Don\'t send an email; write the contents to stdout instead.')
    parser.add_argument('--secrets_path', type=str, help='Path of secrets.yaml file. Defaults to ./secrets.yaml')
    parser.add_argument('--log_path', type=str, help='Path of Reporter log file. Defaults to ./reporter.log')
    parser_args = parser.parse_args()

    log_level = logging.DEBUG if parser_args.debug else logging.ERROR
    log_format = '%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        filename = (parser_args.log_path or os.path.dirname(os.path.realpath(__file__)) + '/reporter.log'),
        level = log_level,
        format = log_format,
        )
    logging.captureWarnings(True)

    logging.debug('Starting Reporter.')

    if parser_args.debug:
        # Add another handler, identical to the first, attached to stdout
        root = logging.getLogger()
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.getLogger().getEffectiveLevel())
        ch.setFormatter(logging.Formatter(log_format))
        root.addHandler(ch)

    # For currency formatting
    locale.setlocale(locale.LC_ALL, '')

    main(parser_args)
    logging.debug('Completed Reporter.')
