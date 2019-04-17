""" GQL Chema for AxGrid and AxColumn manipulation """
import uuid
import graphene
from loguru import logger

from backend.model import AxForm, AxGrid, AxColumn
import backend.model as ax_model
# import backend.cache as ax_cache # TODO use cache!
from backend.schemas.types import Grid, Column, PositionInput
# import ujson as json


class CreateColumn(graphene.Mutation):
    """ Creates AxColumn """
    class Arguments:  # pylint: disable=missing-docstring
        grid_guid = graphene.String()
        field_guid = graphene.String()
        column_type = graphene.String()
        position = graphene.Int()
        positions = graphene.List(PositionInput)

    ok = graphene.Boolean()
    column = graphene.Field(Column)

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info
            grid_guid = args.get('grid_guid')
            field_guid = args.get('field_guid')
            column_type = args.get('column_type')
            position = args.get('position')
            positions = args.get('positions')

            ax_grid = ax_model.db_session.query(AxGrid).filter(
                AxGrid.guid == uuid.UUID(grid_guid)
            ).first()

            ax_column = AxColumn()
            ax_column.grid_guid = ax_grid.guid
            ax_column.field_guid = uuid.UUID(field_guid)
            ax_column.column_type = column_type
            ax_column.position = position
            ax_model.db_session.add(ax_column)

            for column in ax_grid.columns:
                for pos in positions:
                    if column.guid == uuid.UUID(pos.guid):
                        column.position = pos.position
                        column.column_type = pos.parent
                        print(f"position={pos.position} parent={pos.parent}")

            ax_model.db_session.commit()

            ok = True
            return CreateColumn(column=ax_column, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - CreateColumn.')
            raise


class GridsQuery(graphene.ObjectType):
    """Query all data of AxGrid and related classes"""
    grid = graphene.Field(
        Grid,
        form_db_name=graphene.Argument(type=graphene.String, required=True),
        grid_db_name=graphene.Argument(type=graphene.String, required=True)
    )

    async def resolve_grid(self, info, form_db_name, grid_db_name):
        """Get AxGrid by db_name"""

        ax_form = ax_model.db_session.query(AxForm).filter(
            AxForm.db_name == form_db_name
        ).first()

        query = Grid.get_query(info=info)
        grid = query.filter(AxGrid.form_guid == ax_form.guid).filter(
            AxGrid.db_name == grid_db_name).first()
        print(grid.guid)
        return grid


class GridsMutations(graphene.ObjectType):
    """Combine all mutations"""
    create_column = CreateColumn.Field()
