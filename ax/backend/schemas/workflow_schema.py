""" GQL Chema for Workflow manipulation """
import uuid
import graphene
from loguru import logger
import ujson as json

from backend.model import AxForm, AxGrid, AxColumn
import backend.model as ax_model
import backend.schema as ax_schema

# import backend.cache as ax_cache # TODO use cache!
from backend.schemas.types import Grid, Column, PositionInput
# import ujson as json


class CreateState(graphene.Mutation):
    """Create AxState"""
    class Arguments:  # pylint: disable=missing-docstring
        guid = graphene.String()

    ok = graphene.Boolean()

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info
            # ax_form = ax_model.db_session.query(AxForm).filter(
            #     AxForm.guid == uuid.UUID(args.get('guid'))
            # ).first()

            ok = True
            return CreateState(ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - CreateState.')
            raise


class WorkflowQuery(graphene.ObjectType):
    """Query all data of AxGrid and related classes"""
    grid = graphene.Field(
        Grid,
        form_db_name=graphene.Argument(type=graphene.String, required=True),
        grid_db_name=graphene.Argument(type=graphene.String, required=True),
        update_time=graphene.Argument(type=graphene.String, required=False)
    )

    async def resolve_grid(self, info, form_db_name, grid_db_name, update_time=None):
        """Get AxGrid"""
        del update_time
        ax_form = ax_model.db_session.query(AxForm).filter(
            AxForm.db_name == form_db_name
        ).first()

        query = Grid.get_query(info=info)
        grid = query.filter(AxGrid.form_guid == ax_form.guid).filter(
            AxGrid.db_name == grid_db_name).first()
        return grid


class WorkflowMutations(graphene.ObjectType):
    """Combine all mutations"""
    create_state = CreateState.Field()
