from multipart import parse_form
from urllib.parse import parse_qs


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
            headers = {"Content-Type": content_type, "Content-Length": content_length}

            def on_field(field):
                field_name = field.field_name.decode("utf-8")
                value = field.value.decode("utf-8")

                post_parameters[field_name] = value

            def on_file(field):
                field_name = field.field_name.decode("utf-8")
                file_name = field.file_name.decode("utf-8")

                field.file_object.seek(0)
                file_content = field.file_object.read().decode("utf-8")

                post_parameters[field_name] = {
                    "filename": file_name,
                    "content": file_content
                }

            parse_form(headers, env["wsgi.input"], on_field, on_file)

        response_data = {
            "GET Parameters": get_parameters,
            "POST Parameters": post_parameters,
        }

        response_string = f"Parsed Request Data:\n{response_data}"

        response_bytes = response_string.encode("utf-8")

        return [response_bytes]

application = SimpleWSGIApp()
