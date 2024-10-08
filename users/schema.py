# users/schema.py

import graphene
import graphql_jwt
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
from graphql_jwt.shortcuts import create_refresh_token, get_token
class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()

class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)
    token = graphene.String()
    refresh_token = graphene.String()
    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String(required=True)
    def mutate(self, info, username, password, email):
        user = get_user_model()(
            username=username,
            email=email,
        )
        user.set_password(password)
        user.save()
        token = get_token(user)
        refresh_token = create_refresh_token(user)
        return CreateUser(user=user, token=token, refresh_token=refresh_token)


class DeleteUser(graphene.Mutation):
    success = graphene.Boolean()

    class Arguments:
        id = graphene.Int(required=True)

    def mutate(self, info, id):
        try:
            # Получаем модель пользователя
            User = get_user_model()
            # Находим пользователя по имени пользователя
            user = User.objects.get(id=id)
            # Удаляем пользователя
            user.delete()
            return DeleteUser(success=True)
        except User.DoesNotExist:
            return DeleteUser(success=False)




class Query(graphene.ObjectType):
    whoami = graphene.Field(UserType)
    users = graphene.List(UserType)
    def resolve_whoami(self, info):
        user = info.context.user
        # Check if user is authenticated
        if user.is_anonymous:
            raise Exception("Authentication Failure: Your must be signed in")
        return user
    # Check if user is authenticated using decorator
    @login_required
    def resolve_users(self, info):
        return get_user_model().objects.all()

class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    verify_token = graphql_jwt.Verify.Field()
    create_user = CreateUser.Field()
    delete_user = DeleteUser.Field()
    
schema = graphene.Schema(query=Query, mutation=Mutation)

#добавлен класс удаления