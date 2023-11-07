# from src.auth.exceptions import InvalidCredentials
# from src.auth.schemas import AuthUser
# from src.auth.security import check_password, hash_password
# from src.database import auth_user, database, task_result

# async def create_task(user: AuthUser) -> Record | None:
#     insert_query = (
#         insert(task_result)
#         .values(
#             {
#                 "email": user.email,
#                 "password": hash_password(user.password),
#                 "created_at": datetime.utcnow(),
#             }
#         )
#         .returning(auth_user)
#     )

#     return await database.fetch_one(insert_query)
