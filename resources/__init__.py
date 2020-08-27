from flask_restful import Resource


class BaseApi(Resource):
    def get(self, ):
        return 'Welcome to the App'
