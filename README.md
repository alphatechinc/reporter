# Reporter
Reporter is a command line tool for sending data driven HTML reports via email.

## Usage

Send an email report:

        $ reporter --verbose daily_report.yaml
        Successfully emailed Daily Report to 3 recipients.

Configure reports through friendly YAML:

        $ cat daily_report.yaml
        report-name: Daily Report
        query: |
            SELECT
                SUM(amount_cents) AS revenue,
                COUNT(id) AS payments,
                SUM(amount_cents) / COUNT(id) AS mean_payment_size,
                COUNT(DISTINCT user_id) AS active_customers
            FROM
                payments
            WHERE
                payment_dt_utc >= NOW() - INTERVAL 1 DAY
                success = 1
        ordered-column-formats:
            - dollars_millions
            - unitless_thousands
            - dollars
            - unitless_thousands
        recipients:
            - jack@company.com
            - finance@company.com
            - all-reports@company.com


Send an email report daily via `cron` or your favorite job scheduler:

        $ crontab -l
        0 0 * * * /usr/bin/reporter /home/analytics/reporter/daily_report.yaml

