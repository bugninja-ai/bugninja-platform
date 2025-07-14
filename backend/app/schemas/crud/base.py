from faker import Faker
from pydantic import BaseModel, ConfigDict

faker = Faker()


class CreationModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        # TODO! : discuss this with Tomi
        # alias_generator=camelize,
        populate_by_name=True,
    )


class UpdateModel(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        from_attributes=True,
        # TODO! : discuss this with Tomi
        # alias_generator=camelize,
        populate_by_name=True,
    )
