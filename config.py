import logging

from tornado.options import define

define(
    "debug", default=False, type=bool, help="Work in debug mode (should be True for development)"
)
define("port", default=9990, type=int, help="Port to run on")
define("host", default="127.0.0.1", help="Host to run on")
define("base_path", default="", help="Base path to site")

define("log_filename", default=None, help="log filename")
define("log_level", default=logging.DEBUG, help="log level")

define("api_endpoint", type=str, default="https://api.huntflow.ru", help="API URL")
define("api_key", type=str, default="", help="API key")
define("api_account_id", type=int, help="Account to add applicants to")

define("vacancy_id", type=int, help="Huntflow vacancy identifier to add applicants to")
define("source_id", type=int, help="Source of applicant")
define("status_id", type=int, help="Status of applicant")

define("vacancy_og", type=str, default="vacancy.png", help="OG image")
define(
    "vacancy_name",
    type=str,
    default="Моя вакансия",
    help="Human readable vacancy name for page and Open Graph",
)
define(
    "vacancy_url",
    type=str,
    default="https://example.com/career/my-vacancy",
    help="URL to vacancy description page",
)
define(
    "privacy_url",
    type=str,
    default="https://example.com/privacy-policy",
    help="URL to privacy policy page",
)
