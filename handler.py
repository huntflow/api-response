# -*- coding: utf-8 -*-
import json

from tornado.options import options
from tornado.web import MissingArgumentError
from tort.handler import RequestHandler
from tort.util.request import real_ip

from util.formdata import encode_multipart_formdata
from util.lock import Lock, LockException
from util import urljoin


class IndexHandler(RequestHandler):
    locker = Lock()

    field_to_error_name = {
        "first_name": "Имя",
        "last_name": "Фамилия",
        "phone": "Телефон",
        "email": "Электронный адрес",
    }

    def compute_etag(self):
        return

    @staticmethod
    def add_api_headers(headers: dict = None) -> dict:
        if headers is None:
            headers = {}

        headers.update(
            {"Authorization": "Bearer {}".format(options.api_key),}
        )

        return headers

    @staticmethod
    def compose_api_url(path: str) -> str:
        return urljoin(options.api_endpoint, "account", options.api_account_id, path)

    def finish_with_error(
        self, error_text: str = "Не удалось отправить отклик, попробуйте еще раз"
    ):
        self.set_status(400)
        self.finish({"errors": {"common": [error_text]}})

    def get(self):
        self.render(
            "templates/index.html",
            vacancy_name=options.vacancy_name,
            vacancy_url=options.vacancy_url,
            privacy_url=options.privacy_url,
            vacancy_og=options.vacancy_og,
        )

    async def post(self):
        try:
            data = {
                "first_name": self.get_argument("first_name"),
                "last_name": self.get_argument("last_name"),
                "phone": self.get_argument("phone"),
                "email": self.get_argument("email"),
            }
        except MissingArgumentError as e:
            self.finish_with_error(
                'Не заполнено поле "{}"'.format(self.field_to_error_name[e.arg_name])
            )
            return

        lock_key = real_ip(self.request)

        try:
            self.locker.gain_lock(lock_key)
        except LockException:
            self.finish_with_error("Вы отправляете запросы слишком часто. Попробуйте позднее.")
            return

        comment = self.get_argument("comment", None)
        cv_link = self.get_argument("cv", None)
        cv_files = self.request.files.get("cv_file")
        cv_file = None
        if cv_files:
            cv_file = self.request.files["cv_file"][0]

        if cv_file:
            content_type, body = encode_multipart_formdata(
                [], [("file", cv_file["filename"], cv_file["body"])]
            )

            response, parsed_file_data = await self.fetch_request(
                self.make_request(
                    "upload",
                    method="POST",
                    full_url=self.compose_api_url("upload"),
                    headers=self.add_api_headers(
                        {
                            "Content-Type": content_type,
                            "Content-Length": str(len(body)),
                            "X-File-Parse": "true",
                        }
                    ),
                    data=body,
                    allow_ipv6=False,
                    validate_cert=False,
                    request_timeout=5.0,
                )
            )

            if not response.error:
                if parsed_file_data.get("photo"):
                    data["photo"] = parsed_file_data["photo"]["id"]

                fields = parsed_file_data.get("fields")
                if fields:
                    if fields.get("birthdate") and fields["birthdate"].get("precision") == "day":
                        data["birthday_day"] = fields["birthdate"]["day"]
                        data["birthday_month"] = fields["birthdate"]["month"]
                        data["birthday_year"] = fields["birthdate"]["year"]

                    if fields.get("experience"):
                        data["position"] = fields["experience"][0]["position"]
                        data["company"] = fields["experience"][0]["company"]

                    if fields.get("salary"):
                        data["money"] = fields["salary"]

                data["externals"] = [
                    {
                        "data": {
                            "body": "\n\n".join(
                                filter(
                                    None,
                                    [
                                        "Ссылка на резюме: {}".format(cv_link) if cv_link else None,
                                        parsed_file_data.get("text"),
                                    ],
                                )
                            )
                        },
                        "files": [{"id": parsed_file_data["id"]}],
                        "auth_type": "NATIVE",
                        "account_source": options.source_id,
                    }
                ]

        if not data.get("externals"):
            data["externals"] = [
                {
                    "data": {"body": cv_link or ""},
                    "auth_type": "NATIVE",
                    "account_source": options.source_id,
                }
            ]

        response, applicant_data = await self.fetch_request(
            self.make_request(
                "applicant",
                method="POST",
                full_url=self.compose_api_url("applicants"),
                headers=self.add_api_headers(),
                data=json.dumps(data),
                allow_ipv6=False,
                validate_cert=False,
                request_timeout=5.0,
            )
        )

        if response.error:
            self.finish_with_error()
            return

        response, vacancy_applicant_data = await self.fetch_request(
            self.make_request(
                "applicant-vacancy",
                method="POST",
                full_url=self.compose_api_url("applicants/{}/vacancy".format(applicant_data["id"])),
                headers=self.add_api_headers(),
                validate_cert=False,
                allow_ipv6=False,
                data=json.dumps(
                    {
                        "vacancy": options.vacancy_id,
                        "status": options.status_id,
                        "comment": "Сопроводительное письмо: {}".format(comment)
                        if comment
                        else None,
                    }
                ),
            )
        )

        if response.error:
            self.finish_with_error()
            return

        self.finish({"status": "Отлик успешно добавлен"})
