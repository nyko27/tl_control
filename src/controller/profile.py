from fastapi import APIRouter, Depends
from fastapi_jwt_auth import AuthJWT

from src.homeassistant_utils.parse_config import get_entity_ids_from_yaml
from src.schemas.profile import ProfileLogin, ProfileForm, ProfileORM
from src.service.profile_service import ProfileService

profile_router = APIRouter(prefix="/profile", tags=["profile"])


@profile_router.post("/register", response_model=ProfileORM)
async def create_profile(
        profile_data=Depends(ProfileForm.as_form),
        profile_service: ProfileService = Depends(),
):
    decoded_yaml = await profile_data.config_yaml.read()
    ha_entities = get_entity_ids_from_yaml(decoded_yaml)

    new_profile = profile_service.add_profile(
        ha_entities=ha_entities,
        username=profile_data.username,
        password=profile_data.password,
    )
    return new_profile


@profile_router.post("/login")
async def login(
        login_data: ProfileLogin,
        profile_service: ProfileService = Depends(),
        authorize: AuthJWT = Depends(),
):
    profile_service.check_login_data(login_data.username, login_data.password)
    access_token = authorize.create_access_token(subject=login_data.username)
    authorize.set_access_cookies(access_token)
    return {"msg": "Successfully signed in"}


@profile_router.post("/logout")
async def logout(authorize: AuthJWT = Depends()):
    authorize.jwt_required()
    authorize.unset_jwt_cookies()
    return {"msg": "Successfully signed out"}


@profile_router.get("", response_model=ProfileORM)
async def get_profile(
        profile_service: ProfileService = Depends(),
        authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    username = authorize.get_jwt_subject()
    profile = profile_service.get_profile_by_username(username)
    return profile


@profile_router.delete("/delete")
async def delete(
        profile_service: ProfileService = Depends(),
        authorize: AuthJWT = Depends(),
):
    authorize.jwt_required()
    username = authorize.get_jwt_subject()
    profile_service.delete_profile_by_id_or_username(username)
    authorize.unset_jwt_cookies()
    return {"msg": "Successfully deleted profile"}
