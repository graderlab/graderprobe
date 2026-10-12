-- PyPI downloads for graderprobe: trend, geography, installer.
-- Note: the public BigQuery dataset has NO IP and NO User-Agent — only
-- country_code. IP-level attribution, if needed, comes from the documented
-- version-check beacon (see README), not from PyPI.

SELECT
  DATE(t.timestamp)                                        AS day,
  t.file.project                                           AS project,
  t.file.version                                           AS version,
  t.details.installer.name                                 AS installer,
  t.details.python                                         AS python,
  t.details.system.name                                    AS system,
  t.country_code                                           AS country,
  COUNT(*)                                                 AS downloads
FROM `bigquery-public-data.pypi.file_downloads` AS t
WHERE t.file.project = 'graderprobe'
GROUP BY day, project, version, installer, python, system, country
ORDER BY day DESC;
