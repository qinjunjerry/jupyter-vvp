import json

from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic)
from IPython.core.magic_arguments import magic_arguments, argument, parse_argstring

from vvpmagics.vvpsession import VvpSession

print('Loading vvp-vvpmagics.')


def sql_execute_endpoint(namespace):
    return "/sql/v1beta1/namespaces/{}/sqlscripts:execute".format(namespace)


def sql_validate_endpoint(namespace):
    return "/sql/v1beta1/namespaces/{}/sqlscripts:validate".format(namespace)


sql_validate_supported_responses = [
    "VALIDATION_RESULT_VALID_DDL_STATEMENT",
    "VALIDATION_RESULT_VALID_COMMAND_STATEMENT"
]
sql_validate_possible_responses = \
    sql_validate_supported_responses + [
        "VALIDATION_RESULT_INVALID",
        "VALIDATION_RESULT_INVALID_QUERY",
        "VALIDATION_RESULT_UNSUPPORTED_QUERY",
        "VALIDATION_RESULT_VALID_INSERT_QUERY",
        "VALIDATION_RESULT_VALID_SELECT_QUERY"
    ]


def is_invalid_request(response):
    return response.status_code != 200 \
           or json.loads(response.text)['validationResult'] not in sql_validate_possible_responses


def is_supported_sql_command(response):
    return json.loads(response.text)['validationResult'] in sql_validate_supported_responses


@magics_class
class VvpMagics(Magics):

    @line_magic
    @magic_arguments()
    @argument('hostname', type=str, help='Hostname')
    @argument('-p', '--port', type=str, default="8080", help='Port')
    @argument('-n', '--namespace', type=str, help='Namespace. If empty, lists all namespaces.')
    @argument('-s', '--session', type=str, help='Session name')
    @argument('-f', '--force', type=bool, help='Force updating of session names.')
    def connect_vvp(self, line):
        args = parse_argstring(self.connect_vvp, line)
        hostname = args.hostname
        port = args.port
        vvp_base_url = "http://{}:{}".format(hostname, port)

        if args.namespace:
            session_name = args.session or VvpSession.default_session_name
            force_update = args.force or False
            if session_name is None:
                raise Exception("No session name given and none already exist.")
            return VvpSession.create_session(vvp_base_url, args.namespace, session_name, force=force_update)
        else:
            return VvpSession.get_namespaces(vvp_base_url)

    @cell_magic
    @magic_arguments()
    @argument('-s', '--session', type=str, help='Name of the object representing the connection '
                                                'to a given vvp namespace.')
    def flink_sql(self, line, cell):
        args = parse_argstring(self.flink_sql, line)
        session = VvpSession.get_session(args.session)

        if cell:
            validation_response = self.validate_sql(cell, session)
            if is_invalid_request(validation_response):
                raise FlinkSqlRequestException("Bad HTTP request or incompatible VVP back-end.", sql=cell)
            if is_supported_sql_command(validation_response):
                execute_command_response = self.execute_sql(cell, session)
                return json.loads(execute_command_response.text)
            else:
                raise SqlSyntaxException("Invalid or unsupported SQL statement.", sql=cell)
        else:
            print("Empty cell: doing nothing.")

    @staticmethod
    def validate_sql(cell, session):
        validate_endpoint = sql_validate_endpoint(session.get_namespace())
        body = json.dumps({"script": cell})
        validation_response = session.submit_post_request(validate_endpoint, body)
        return validation_response

    @staticmethod
    def execute_sql(cell, session):
        execute_endpoint = sql_execute_endpoint(session.get_namespace())
        body = json.dumps({"statement": cell})
        execute_response = session.submit_post_request(execute_endpoint, body)
        return execute_response


class SqlSyntaxException(Exception):

    def __init__(self, message="", sql=None):
        self.message = message
        self.sql = sql


class FlinkSqlRequestException(Exception):

    def __init__(self, message="", sql=None):
        self.message = message
        self.sql = sql
