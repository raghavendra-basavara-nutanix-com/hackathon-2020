import os
import connexion
from connexion.resolver import RestyResolver
from flask_cors import CORS
from api.controllers import get_resolvers
from flask import render_template
SPECIFICATION_DIR_PATH = "./swagger/"
SERVICE_APP_SWAGGER_FILE_NAME = "app.yml"
app = connexion.App(__name__, specification_dir=SPECIFICATION_DIR_PATH,
                    options={"swagger_ui": False}
                    )
app_resolvers = get_resolvers()
app.add_api(SERVICE_APP_SWAGGER_FILE_NAME,
            resolver=app_resolvers.get,
            options={
                "swagger_ui": True
            }
        )
CORS(app.app)
# class Server:
#     """
#     Application server serving APIs defined by swagger docs
#     """
#
#     SPECIFICATION_DIR_PATH = "./swagger/"
#     SERVICE_APP_SWAGGER_FILE_NAME = "app.yml"
#
#     def __init__(self):
#         self.app = connexion.App(__name__, specification_dir=self.SPECIFICATION_DIR_PATH,
#                                  options={"swagger_ui": False}
#                                  )
#         app_resolvers = get_resolvers()
#         self.app.add_api(
#             self.SERVICE_APP_SWAGGER_FILE_NAME,
#             resolver=app_resolvers.get,
#             options={
#                 "swagger_ui": True
#             }
#         )
#
#     def run(self):
#         """
#         Start application server
#         """
#         CORS(self.app.app)
#         self.app.run(port=int(os.environ.get('PORT', 2020)))
# Create a URL route in our application for "/"
@app.route('/')
def home():
    """
    This function just responds to the browser ULR
    localhost:5000/
    :return:        the rendered template 'home.html'
    """
    return render_template('home.html')
# if __name__ == '__main__':
#     # run standalone server
#     SERVER = Server()
#     SERVER.run()
if __name__ == '__main__':
    # run standalone server
    app.run(port=int(os.environ.get('PORT', 2020)))