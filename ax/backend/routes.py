"""All routes of ax-core and ax-admin"""

import os
import sys
import asyncio
import uuid

from sanic import response
from loguru import logger
import aiopubsub
from graphql_ws.websockets_lib import WsLibSubscriptionServer
from sanic_graphql import GraphQLView
from graphql.execution.executors.asyncio import AsyncioExecutor
import ujson as json

import backend.cache as ax_cache
import backend.schema as ax_schema
import backend.misc as ax_misc
import backend.pubsub as ax_pubsub
from backend.tus import tus_bp
import backend.model as ax_model
from backend.model import AxForm, AxField
import backend.schemas.form_schema as form_schema
# import backend.scheduler as ax_scheduler
import backend.dialects as ax_dialects

this = sys.modules[__name__]

loop = asyncio.new_event_loop()
actions_loop = asyncio.new_event_loop()
app = None
graphql_view = None
dummy_view = None


class AxGraphQLView(GraphQLView):
    """ Extends GraphQLView to output GQL errors and schema updates"""

    def __init__(self, **kwargs):
        super().__init__(schema=ax_schema.schema,
                         graphiql=False,
                         enable_async=True,
                         executor=AsyncioExecutor(loop=this.loop))

    @staticmethod
    def format_error(error):
        """ This method is required for showing graphql errors """
        logger.error(error)
        return GraphQLView.format_error(error)


def init_graphql_view():  # pylint: disable=unused-variable
    """Initiate graphql"""
    this.graphql_view = AxGraphQLView.as_view()
    this.app.add_route(this.graphql_view, '/api/graphql')


# async def do_action():
#     """ Test function """
#     from backend.schema import schema

#     values = {
#         "searchString": "Chateau Lafite Rothschild 1996",
#         "supplier": "9c198568469447268d62b395badeb71f",
#         "loader": "0eb38c45e9954442995c6205f2e3f7eb"
#     }

#     query = f"""
#         mutation(
#             $formDbName: String,
#             $actionDbName: String,
#             $values: String
#         ){{
#             doAction(
#                 formDbName: $formDbName
#                 actionDbName: $actionDbName
#                 values: $values
#             ) {{
#                 form {{
#                 guid
#                 dbName
#                 }}
#                 newGuid
#                 messages
#                 ok
#             }}
#         }}
#     """
#     variables = {
#         "formDbName": "Stock",
#         "actionDbName": "addDraft",
#         "values": json.dumps(values)
#     }
#     result = schema.execute(query, variables=variables)
#     test_str = json.dumps(result.data, sort_keys=True, indent=4)
#     print(test_str)


def init_routes(sanic_app):
    """Innitiate all Ax routes"""
    try:
        # Add tus upload blueprint
        sanic_app.blueprint(tus_bp)
        # Add web-socket subscription server
        subscription_server = WsLibSubscriptionServer(ax_schema.schema)

        @sanic_app.route(
            '/api/file/<form_guid>/<row_guid>/<field_guid>/<file_name>',
            methods=['GET'])
        async def db_file_viewer(   # pylint: disable=unused-variable
                request, form_guid, row_guid, field_guid, file_name):  # pylint: disable=unused-variable
            """ Used to display files that are stored in database.
                Used in fields like AxImageCropDb"""
            del request, form_guid, file_name
            safe_row_guid = str(uuid.UUID(str(row_guid)))
            ax_field = ax_model.db_session.query(AxField).filter(
                AxField.guid == uuid.UUID(field_guid)
            ).first()
            field_value = await ax_dialects.dialect.select_field(
                form_db_name=ax_field.form.db_name,
                field_db_name=ax_field.db_name,
                row_guid=safe_row_guid)
            return response.raw(
                field_value, content_type='application/octet-stream')

        @sanic_app.route(
            '/api/file/<form_guid>/<row_guid>/<field_guid>/<file_guid>/<file_name>',    # pylint: disable=line-too-long
            methods=['GET'])
        async def file_viewer(  # pylint: disable=unused-variable
                request, form_guid, row_guid, field_guid, file_guid, file_name):
            """ Used to display files uploaded and stored on disk.
                Displays temp files too. Used in all fields with upload"""
            del request

            # if row_guid is null -> display from /tmp without permissions
            if not row_guid or row_guid == 'null':
                tmp_dir = os.path.join(ax_misc.tmp_root_dir, file_guid)
                file_name = os.listdir(tmp_dir)[0]
                temp_path = os.path.join(tmp_dir, file_name)
                return await response.file(temp_path)

            # get AxForm with row values
            ax_form = ax_model.db_session.query(AxForm).filter(
                AxForm.guid == uuid.UUID(form_guid)
            ).first()
            ax_form = await form_schema.set_form_values(
                ax_form=ax_form, row_guid=row_guid)

            # Get values from row, field
            field_values = None
            for field in ax_form.fields:
                if field.guid == uuid.UUID(field_guid):
                    if field.value:
                        field_values = json.loads(field.value)

            # Find requested file in value
            the_file = None
            for file in field_values:
                if file['guid'] == file_guid:
                    the_file = file

            if not the_file:
                return response.text("", status=404)

            # if file exists -> return file
            row_guid_str = str(uuid.UUID(row_guid))
            file_path = os.path.join(
                ax_misc.uploads_root_dir,
                'form_row_field_file',
                form_guid,
                row_guid_str,
                field_guid,
                the_file['guid'],
                the_file['name'])
            if not os.path.lexists(file_path):
                return response.text("", status=404)
            return await response.file(file_path)

        @sanic_app.route('/admin/<path:path>')
        def index(request, path):  # pylint: disable=unused-variable
            """ This is MAIN ROUTE. (except other routes listed in this module).
                All requests are directed to Vue single page app. After that Vue
                handles routing."""
            del request, path
            absolute_path = ax_misc.path('dist/ax/index.html')
            return response.html(open(absolute_path).read())

        @sanic_app.route('/')
        def handle_request():  # pylint: disable=unused-variable
            return response.redirect('/deck')

        @sanic_app.route('/draw_ax')
        async def draw_ax(request):  # pylint: disable=unused-variable
            """ Outputs bundle.js. Used when Ax web-components
                are inputed somewhere. Users can use this url for <script> tag
                """
            del request
            absolute_path = ax_misc.path('dist/ax/static/js/ax-bundle.js')
            return await response.file(
                absolute_path,
                headers={
                    'Content-Type': 'application/javascript; charset=utf-8'
                }
            )

        @sanic_app.websocket('/api/subscriptions', subprotocols=['graphql-ws'])
        async def subscriptions(request, web_socket):  # pylint: disable=unused-variable
            """Web socket route for graphql subscriptions"""
            del request
            try:
                # TODO: Why socket error exception occurs without internet
                await subscription_server.handle(web_socket)
                return web_socket
            except asyncio.CancelledError:
                pass
                # logger.exception('Socket error')

        @sanic_app.route('/api/test')
        async def test(request):  # pylint: disable=unused-variable
            """Test function"""
            del request
            this.test_schema = 'IT WORKS'
            ax_pubsub.publisher.publish(
                aiopubsub.Key('dummy_test'), this.test_schema)
            return response.text(this.test_schema)

        @sanic_app.route('/api/set')
        async def cache_set(request):  # pylint: disable=unused-variable
            """Cache Test function"""
            del request
            obj = ['one', 'two', 'three']
            await ax_cache.cache.set('user_list', obj)
            return response.text('Cache SET' + str(obj))

        @sanic_app.route('/api/get')
        async def cache_get(request):  # pylint: disable=unused-variable
            """Cache Test function"""
            del request
            obj = await ax_cache.cache.get('user_list')
            ret_str = 'READ cache == ' + \
                str(obj[0].username + ' - ' + os.environ['AX_VERSION'])
            return response.text(ret_str)

    except Exception:
        logger.exception('Error initiating routes.')
        raise
