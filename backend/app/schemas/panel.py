from typing import Optional, List
from pydantic import BaseModel

class WidgetBase(BaseModel):
    type: str
    title: str
    is_system: bool = False
    grid_col: int = 1
    grid_row: int = 1
    col_span: int = 1
    row_span: int = 1
    config: str = "{}"

class WidgetCreate(WidgetBase):
    pass

class WidgetUpdate(BaseModel):
    title: Optional[str] = None
    grid_col: Optional[int] = None
    grid_row: Optional[int] = None
    col_span: Optional[int] = None
    row_span: Optional[int] = None
    config: Optional[str] = None

class WidgetResponse(WidgetBase):
    id: int
    panel_id: int

    class Config:
        from_attributes = True

class PanelBase(BaseModel):
    name: str
    description: Optional[str] = ""
    is_default: bool = False

class PanelCreate(PanelBase):
    pass

class PanelUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None

class PanelCloneRequest(BaseModel):
    target_user_id: Optional[int] = None
    new_panel_name: str

class PanelResponse(PanelBase):
    id: int
    owner_id: Optional[int] = None
    is_system_template: bool
    widgets: List[WidgetResponse] = []

    class Config:
        from_attributes = True
