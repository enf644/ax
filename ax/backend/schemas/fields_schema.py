"""This is part of GraphQL schema (Mutaions, Queryes, Subscriptions).
Defines Fields Scheme and all mutations.
Will be used for mutations used in field_types"""

import graphene
from graphene_sqlalchemy.converter import convert_sqlalchemy_type
from backend.misc import convert_column_to_string
from backend.model import GUID

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


class FieldsMutations(graphene.ObjectType):
    """Contains all AxUser mutations"""
    mutation_example = MutationExample.Field()
