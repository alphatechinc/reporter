# Reporter
Reporter is a command line tool for sending data driven HTML reports via email.

## Usage

Send an email report:

        $ reporter --verbose daily_report.yaml
        Successfully emailed Daily Report to 3 recipients.

Configure reports through friendly YAML:

        $ cat daily_sales_summary.yaml
        report-name: Company.com Daily Sales Summary
        email-from: analytics-team@company.com
        recipients:
            - jack@company.com
            - finance@company.com
            - all-reports@company.com
        query-file: daily_sales_summary.sql

The report itself is a friendly SQL query, with suffixes denoting format preference:

        $ cat daily_sales_summary.sql
        SELECT
            SUM(amount_cents) / 100 AS revenue__dollars_millions,
            COUNT(id) AS payments__number,
            SUM(amount_cents) / COUNT(id) AS mean_payment__dollars_cents,
            COUNT(DISTINCT user_id) AS active_customers__number_thousands
        FROM
            payments
        WHERE
            payment_dt_utc >= NOW() - INTERVAL 1 DAY
            success = 1

Send an email report daily via `cron` or your favorite job scheduler:

        $ crontab -l
        0 0 * * * /usr/bin/reporter /home/analytics/reporter/daily_report.yaml

