from multipart import parse_form
from urllib.parse import parse_qs


STATUS_OK = 200

class SimpleWSGIApp:
    def __init__(self):
        ...

    def __call__(self, env, start_response):
        start_response("200 OK", [("Content-Type", "text/plain")])

        get_parameters = parse_qs(env.get("QUERY_STRING", ""))
        post_parameters = {}

        content_type = env.get("CONTENT_TYPE", "")
        content_length = int(env.get("CONTENT_LENGTH", 0))

        if content_length > 0:
            headers = {"Content-Type": content_type}

            def on_field(name, value, headers):
                name_string = name.decode()
                post_parameters[name_string] = value.decode("utf-8")

            def on_file(name, value, headers):
                name_string = name.decode()
                post_parameters[name_string] = {
                    "filename": headers["filename"],
                    "content": value
                }


            data_iterator = parse_form(headers,
                env["wsgi.input"],
                on_field,
                on_file
            )

        response_data = {
            "GET Parameters": get_parameters,
            "POST Parameters": post_parameters,
        }

        response_string = f"Parsed Request Data:\n{response_data}"

        response_bytes = response_string.encode("utf-8")

        return [response_bytes]

application = SimpleWSGIApp()
