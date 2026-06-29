from pydantic import BaseModel, ConfigDict


class AreaSummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    name: str
    district_name: str
    administrative_dong_name: str
    is_mock: bool


class AreaListResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    items: list[AreaSummary]


class CategorySummary(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    code: str
    name: str
    group_name: str
    similarity_group: str


class CategoryListResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    items: list[CategorySummary]

