#!/usr/bin/env python
# -*- coding: utf-8 -*-


from weakref import WeakKeyDictionary
import abc
import json
import datetime
import logging
import hashlib
import uuid
from optparse import OptionParser
from http.server import HTTPServer, BaseHTTPRequestHandler
from scoring import get_score, get_interests
import store

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}
# NULL_VALUES = ['', None, {}, [], ()]


class BaseData():
    def __init__(self, required=False, nullable=False):
        self.required = required
        self.nullable = nullable
        self.data = WeakKeyDictionary()

    def __get__(self, instance, owner):
        return self.data.get(instance)  # , self.default

    def __set__(self, instance, value):
        value = self.validate(value)
        self.data[instance] = value

    def validate(self, value):

        #print('BaseData_valid')

        if self.required and value is None:
            raise ValueError('value is required')
        if not self.nullable and value is None:
            raise ValueError('value cannot be nullable')

        return value


class CharField(BaseData):
    def validate(self, value):
        value = super(CharField, self).validate(value)
        if value is None:
            return value
        if value is not None and not isinstance(value, str):
            raise ValueError('Char value must be str')

        return value


class ArgumentsField(BaseData):
    def validate(self, value):
        value = super(ArgumentsField, self).validate(value)
        if value is not None and not isinstance(value, dict):
            raise ValueError('Arguments value must be dict')

        return value


class EmailField(BaseData):
    def validate(self, value):
        value = super(EmailField, self).validate(value)
        if value is None:
            return value
        if not isinstance(value, str) or '@' not in value:
            raise ValueError('Email value must be str and contain @')

        return value


class PhoneField(BaseData):
    def validate(self, value):
        value = super(PhoneField, self).validate(value)
        if value is None:
            return value
        # value = str(value)
        if not str(value).isdigit() or len(str(value)) != 11 or str(value)[0] != '7':
            raise ValueError('Phone value contain only digits ,startwith 7 and lenght 11 ')

        return value


class DateField(BaseData):
    def validate(self, value):
        value = super(DateField, self).validate(value)
        if value is None:
            return value

        try:
            return datetime.datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError('Date value must have format like DD.MM.YYYY')


class BirthDayField(DateField):
    def validate(self, value):
        value = super(BirthDayField, self).validate(value)
        if value is None:
            return value
        age = datetime.datetime.now() - value
        if age.days / 365 > 70:
            raise ValueError("age >  70")

        return value


class GenderField(BaseData):
    def validate(self, value):
        value = super(GenderField, self).validate(value)
        if value is None:
            return value

        if value is not None and value not in [0, 1, 2]:  # not isinstance(value, int)
            raise ValueError('Gender value must be in [0,1,2]')

        return value


class ClientIDsField(BaseData):
    def validate(self, value):
        if self.required and value in [None, []]:
            raise ValueError('value is required')

        if not isinstance(value, list):
            raise ValueError('ClientID value must be list')
        if not all(isinstance(i, int) for i in value):
            raise ValueError('ClientID values must be int')

        return value


##########################################################################################

class MetaClassRequest(type):
    def __init__(cls, name, bases, attrs):
        super(MetaClassRequest, cls).__init__(name, bases, attrs)
        cls.fields = []
        for k, v in attrs.items():
            if isinstance(v, BaseData):
                v.name = k
                cls.fields.append(v)


class Request(metaclass=MetaClassRequest):
    def __init__(self, request=None):
        self.request = request
        self.error_text = None
        self.correct = True

    def check_request(self):
        return self.correct

    def get_not_empty_fields(self):
        not_empty_fields = [k.name for k in self.fields if getattr(self, k.name) is not None]
        return not_empty_fields


##########################################################################################

class ClientsInterestsRequest(Request):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)

    def __init__(self, client_ids = None, date = None):
        super(ClientsInterestsRequest, self).__init__()
        try:
            self.client_ids = client_ids
            self.date = date
        except ValueError as er:
            self.error_text = str(er)
            self.correct = False


class OnlineScoreRequest(Request):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def __init__(self, first_name=None, last_name=None, email=None, phone=None, birthday=None, gender=None):
        super(OnlineScoreRequest, self).__init__()
        try:
            self.first_name = first_name
            self.last_name = last_name
            self.email = email
            self.phone = phone
            self.birthday = birthday
            self.gender = gender
        except ValueError as er:
            self.error_text = str(er)
            self.correct = False

    def check_request(self):
        check_pairs = []
        check_pairs.append(self.phone is not None and self.email is not None)
        check_pairs.append(self.first_name is not None and self.last_name is not None)
        check_pairs.append(self.gender is not None and self.birthday is not None)
        if not any(check_pairs):
            self.correct = False
            self.error_text = 'incorrect data'
        return self.correct


class MethodRequest(Request):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    def __init__(self, account=None, login=None, token=None, arguments=None,
                 method=None):
        super(MethodRequest, self).__init__()
        try:
            self.account = account
            self.login = login
            self.token = token
            self.arguments = arguments
            self.method = method
        except ValueError as er:
            self.error_text = str(er)
            self.correct = False

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


#################################################################################################


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512(bytes(datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT, "utf-8")).hexdigest()
    else:
        digest = hashlib.sha512(bytes(request.account + request.login + SALT, "utf-8")).hexdigest()
    if digest == request.token:
        return True
    return False


def process_OnlineScoreRequest(request, ctx, store):
    r = OnlineScoreRequest(**request.arguments)
    if not r.check_request():
        return r.error_text, INVALID_REQUEST

    if request.is_admin:
        score = 42
    else:
        score = get_score(store, r.phone, r.email, r.birthday, r.gender, r.first_name, r.last_name)
    ctx["has"] = r.get_not_empty_fields()
    return {"score": score}, OK


def process_ClientsInterestsRequest(request, ctx, store):
    r = ClientsInterestsRequest(**request.arguments)
    if not r.check_request():
        return r.error_text, INVALID_REQUEST

    ctx["nclients"] = len(r.client_ids)
    response_body = {cid: get_interests(store, cid) for cid in r.client_ids}

    return response_body, OK


def method_handler(request, ctx, store):
    method_request = MethodRequest(**request['body'])

    if not method_request.check_request():
        return method_request.error_text, INVALID_REQUEST

    if not check_auth(method_request):
        return None, FORBIDDEN

    if method_request.method == 'online_score':
        response, code = process_OnlineScoreRequest(method_request, ctx, store)
    elif method_request.method == 'clients_interests':
        response, code = process_ClientsInterestsRequest(method_request, ctx, store)
    else:
        return 'unexpected method', INVALID_REQUEST

    return response, code


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = None

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            data_string = data_string.decode("utf-8")
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
