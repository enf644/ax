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

            ax_model.db_session.commit()

            ok = True
            return CreateColumn(column=ax_column, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - CreateColumn.')
            raise


class DeleteColumn(graphene.Mutation):
    """ Deletes AxColumn """
    class Arguments:  # pylint: disable=missing-docstring
        guid = graphene.String()

    ok = graphene.Boolean()
    deleted = graphene.String()

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info
            guid = args.get('guid')

            ax_column = ax_model.db_session.query(AxColumn).filter(
                AxColumn.guid == uuid.UUID(guid)
            ).first()
            ax_model.db_session.delete(ax_column)
            ax_model.db_session.commit()

            ok = True
            return DeleteColumn(deleted=guid, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - DeleteColumn.')
            raise


class ChangeColumnsPositions(graphene.Mutation):
    """Change position and type of columns"""
    class Arguments:  # pylint: disable=missing-docstring
        grid_guid = graphene.String()
        positions = graphene.List(PositionInput)

    ok = graphene.Boolean()
    columns = graphene.List(Column)

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            grid_guid = args.get('grid_guid')
            positions = args.get('positions')

            ax_grid = ax_model.db_session.query(AxGrid).filter(
                AxGrid.guid == uuid.UUID(grid_guid)
            ).one()

            for column in ax_grid.columns:
                for pos in positions:
                    if column.guid == uuid.UUID(pos.guid):
                        column.position = pos.position
                        column.column_type = pos.parent

            ax_model.db_session.commit()
            query = Column.get_query(info)
            column_list = query.filter(
                AxColumn.grid_guid == uuid.UUID(grid_guid)
            ).all()

            ok = True
            return ChangeColumnsPositions(columns=column_list, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - ChangeColumnsPositions.')
            raise


class CreateGrid(graphene.Mutation):
    """ Creates AxGrid """
    class Arguments:  # pylint: disable=missing-docstring
        form_guid = graphene.String()
        name = graphene.String()

    ok = graphene.Boolean()
    grid = graphene.Field(Grid)

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info
            form_guid = args.get('form_guid')
            name = args.get('name')

            ax_form = ax_model.db_session.query(AxForm).filter(
                AxForm.guid == uuid.UUID(args.get('form_guid'))
            ).first()

            db_name = "grid_"
            cur_num = 1
            name_is_checked = False
            while name_is_checked is False:
                error_flag = False
                if cur_num > 1:
                    cur_name = name + " " + str(cur_num)
                else:
                    cur_name = name
                cur_db_name = db_name + str(cur_num)
                for grid in ax_form.grids:
                    if grid.name == cur_name or grid.db_name == cur_db_name:
                        error_flag = True
                if error_flag is True:
                    cur_num = cur_num + 1
                else:
                    name_is_checked = True
                    break

            ax_grid = AxGrid()
            ax_grid.name = cur_name
            ax_grid.form_guid = ax_form.guid
            ax_grid.position = len(ax_form.grids) + 1
            ax_grid.options_json = '{}'
            ax_grid.is_default_view = False
            ax_model.db_session.add(ax_grid)
            ax_model.db_session.commit()

            ok = True
            return CreateGrid(grid=ax_grid, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - CreateGrid.')
            raise


class DeleteGrid(graphene.Mutation):
    """ Deletes AxFGrid """
    class Arguments:  # pylint: disable=missing-docstring
        guid = graphene.String()

    ok = graphene.Boolean()
    deleted = graphene.String()

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info
            guid = args.get('guid')

            ax_grid = ax_model.db_session.query(AxGrid).filter(
                AxGrid.guid == uuid.UUID(guid)
            ).first()
            ax_model.db_session.delete(ax_grid)
            ax_model.db_session.commit()

            ok = True
            return DeleteGrid(deleted=guid, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - DeleteGrid.')
            raise


class UpdateGrid(graphene.Mutation):
    """ Creates AxGrid """
    class Arguments:  # pylint: disable=missing-docstring
        guid = graphene.String()
        name = graphene.String()
        db_name = graphene.String()
        options_json = graphene.String()
        is_default_view = graphene.Boolean()

    ok = graphene.Boolean()
    grid = graphene.Field(Grid)

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info
            guid = args.get('guid')
            name = args.get('name')
            db_name = args.get('db_name')
            options_json = args.get('options_json')
            is_default_view = args.get('is_default_view')

            ax_grid = ax_model.db_session.query(AxGrid).filter(
                AxGrid.guid == uuid.UUID(args.get('guid'))
            ).first()

            if name:
                ax_grid.name = name

            if db_name:
                ax_grid.db_name = db_name

            if options_json:
                ax_grid.options_json = options_json

            if is_default_view:
                ax_grid.is_default_view = is_default_view

            ax_model.db_session.commit()

            ok = True
            return CreateGrid(grid=ax_grid, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - UpdateGrid.')
            raise


class GridsQuery(graphene.ObjectType):
    """Query all data of AxGrid and related classes"""
    grid = graphene.Field(
        Grid,
        form_db_name=graphene.Argument(type=graphene.String, required=True),
        grid_db_name=graphene.Argument(type=graphene.String, required=True)
    )

    grid_data = graphene.Field(
        Grid,
        form_db_name=graphene.Argument(type=graphene.String, required=True),
        grid_db_name=graphene.Argument(type=graphene.String, required=True)
    )

    grids_list = graphene.List(
        Grid,
        form_db_name=graphene.Argument(type=graphene.String, required=True)
    )

    async def resolve_grid(self, info, form_db_name, grid_db_name):
        """Get AxGrid"""

        ax_form = ax_model.db_session.query(AxForm).filter(
            AxForm.db_name == form_db_name
        ).first()

        query = Grid.get_query(info=info)
        grid = query.filter(AxGrid.form_guid == ax_form.guid).filter(
            AxGrid.db_name == grid_db_name).first()
        return grid

    async def resolve_grid_data(self, info, form_db_name, grid_db_name):
        """Get AxGrid"""

        ax_form = ax_model.db_session.query(AxForm).filter(
            AxForm.db_name == form_db_name
        ).first()

        query = Grid.get_query(info=info)
        grid = query.filter(AxGrid.form_guid == ax_form.guid).filter(
            AxGrid.db_name == grid_db_name).first()
        return grid

    async def resolve_grids_list(self, info, form_db_name):
        """Gets list of all AxGrid of form """

        ax_form = ax_model.db_session.query(AxForm).filter(
            AxForm.db_name == form_db_name
        ).first()

        query = Grid.get_query(info=info)
        grids = query.filter(AxGrid.form_guid == ax_form.guid).all()
        return grids


class GridsMutations(graphene.ObjectType):
    """Combine all mutations"""
    create_column = CreateColumn.Field()
    delete_column = DeleteColumn.Field()
    change_columns_positions = ChangeColumnsPositions.Field()
    create_grid = CreateGrid.Field()
    delete_grid = DeleteGrid.Field()
    update_grid = UpdateGrid.Field()
