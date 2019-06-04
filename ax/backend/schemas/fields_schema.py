"""Defines Fields Scheme and all mutations"""

import asyncio
import graphene
# from graphene import relay
from graphene_sqlalchemy import SQLAlchemyConnectionField
from graphene_sqlalchemy.converter import convert_sqlalchemy_type
import aiopubsub
from loguru import logger

from backend.misc import convert_column_to_string
from backend.model import AxUser, GUID
import backend.model as ax_model
import backend.cache as ax_cache
import backend.pubsub as ax_pubsub
from backend.schemas.types import User

convert_sqlalchemy_type.register(GUID)(convert_column_to_string)


class MutationExample(graphene.Mutation):
    """Mutation example"""
    class Arguments:  # pylint: disable=missing-docstring
        input_text = graphene.String()

    output_text = graphene.String()

    async def mutate(self, info, input_text):  # pylint: disable=missing-docstring
        del info
        return MutationExample(output_text=input_text)


class FieldsQuery(graphene.ObjectType):
    """AxUser queryes"""
    pass


class FieldsMutations(graphene.ObjectType):
    """Contains all AxUser mutations"""
    mutation_example = MutationExample.Field()
