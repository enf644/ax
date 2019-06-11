""" GQL Chema for AxGrid and AxColumn manipulation """
import uuid
import graphene
from loguru import logger
import ujson as json

from backend.model import AxForm, AxGrid, AxColumn, AxField
import backend.model as ax_model
import backend.schema as ax_schema

# import backend.cache as ax_cache # TODO use cache!
from backend.schemas.types import Grid, Column, PositionInput
# import ujson as json


def tom_sync_grid(form_db_name, old_db_name, new_db_name):
    """ find all relation AxFields
    for each - check if options contain old form and old grid. If so - replace
    """
    relation_fields = ax_model.db_session.query(AxField).filter(
        AxField.field_type_tag.in_(('Ax1to1', 'Ax1tom', 'Ax1tomTable'))
    ).all()
    for field in relation_fields:
        if 'form' in field.options.keys() and 'grid' in field.options.keys():
            if field.options['grid'] == old_db_name and \
                    field.options['form'] == form_db_name:

                new_options = field.options
                new_options['grid'] = new_db_name

                field.options_json = json.dumps(new_options)
                ax_model.db_session.commit()


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
                    if str(column.guid) == pos.guid:
                        column.position = pos.position
                        column.column_type = pos.parent

            ax_model.db_session.commit()

            ok = True
            return CreateColumn(column=ax_column, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - CreateColumn.')
            raise


class UpdateColumnOptions(graphene.Mutation):
    """Updates options of column"""
    class Arguments:  # pylint: disable=missing-docstring
        guid = graphene.String()
        options = graphene.String()

    ok = graphene.Boolean()

    async def mutate(self, info, **args):  # pylint: disable=missing-docstring
        try:
            del info
            ax_column = ax_model.db_session.query(AxColumn).filter(
                AxColumn.guid == uuid.UUID(args.get('guid'))
            ).first()
            ax_column.options_json = args.get('options')
            ax_model.db_session.commit()

            return UpdateColumnOptions(ok=True)
        except Exception:
            logger.exception('Error in gql mutation - UpdateColumnOptions.')
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
                AxForm.guid == uuid.UUID(form_guid)
            ).first()

            db_name = "Grid"
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
            ax_grid.db_name = db_name + str(cur_num)
            ax_grid.form_guid = ax_form.guid
            ax_grid.position = len(ax_form.grids) + 1

            default_options = {
                "enableQuickSearch": False,
                "enableFlatMode": False,
                "enableColumnsResize": True,
                "enableFiltering": True,
                "enableSorting": True,
                "enableOpenForm": True,
                "enableActions": True,
                "rowHeight": 45,
                "pinned": 0
            }

            ax_grid.options_json = json.dumps(default_options)
            ax_grid.is_default_view = False
            ax_model.db_session.add(ax_grid)
            ax_model.db_session.commit()

            ax_schema.init_schema()

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
            form_db_name = ax_grid.form.name
            old_grid_db_name = ax_grid.db_name
            default_db_name = None

            for grid in ax_grid.form.grids:
                if grid.is_default_view:
                    default_db_name = grid.db_name

            ax_model.db_session.delete(ax_grid)
            ax_model.db_session.commit()

            ax_schema.init_schema()

            tom_sync_grid(
                form_db_name=form_db_name,
                old_db_name=old_grid_db_name,
                new_db_name=default_db_name)

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
            schema_reload_needed = False
            tom_sync_needed = False

            ax_grid = ax_model.db_session.query(AxGrid).filter(
                AxGrid.guid == uuid.UUID(guid)
            ).first()
            old_db_name = ax_grid.db_name

            if name:
                ax_grid.name = name

            if db_name:
                ax_grid.db_name = db_name
                schema_reload_needed = True
                if old_db_name != db_name:
                    tom_sync_needed = True

            if options_json:
                ax_grid.options_json = options_json

            if is_default_view:
                all_grids = ax_model.db_session.query(AxGrid).filter(
                    AxGrid.form_guid == ax_grid.form_guid and
                    AxGrid.guid != ax_grid.guid
                ).all()

                for grid in all_grids:
                    grid.is_default_view = False

                ax_grid.is_default_view = is_default_view
                schema_reload_needed = True

            ax_model.db_session.commit()

            if schema_reload_needed:
                ax_schema.init_schema()

            if tom_sync_needed:
                tom_sync_grid(
                    form_db_name=ax_grid.form.db_name,
                    old_db_name=old_db_name,
                    new_db_name=ax_grid.db_name)

            ok = True
            return UpdateGrid(grid=ax_grid, ok=ok)
        except Exception:
            logger.exception('Error in gql mutation - UpdateGrid.')
            raise


class GridsQuery(graphene.ObjectType):
    """Query all data of AxGrid and related classes"""
    grid = graphene.Field(
        Grid,
        form_db_name=graphene.Argument(type=graphene.String, required=True),
        grid_db_name=graphene.Argument(type=graphene.String, required=True),
        update_time=graphene.Argument(type=graphene.String, required=False)
    )

    # grid_data = graphene.Field(
    #     Grid,
    #     form_db_name=graphene.Argument(type=graphene.String, required=True),
    #     grid_db_name=graphene.Argument(type=graphene.String, required=True),
    #     update_time=graphene.Argument(type=graphene.String, required=False)
    # )

    grids_list = graphene.List(
        Grid,
        form_db_name=graphene.Argument(type=graphene.String, required=True)
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

        # if field is_virtual - we must switch current dbName with field_type.default_db_name
        for column in grid.columns:
            if column.field.field_type.is_virtual:
                column.field.db_name = column.field.field_type.default_db_name

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
