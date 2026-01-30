"""Clothing item schemas for API requests/responses."""

from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, computed_field

from app.utils.signed_urls import sign_image_url


class ItemTags(BaseModel):
    """Tags structure for clothing items."""

    colors: list[str] = Field(default_factory=list)
    primary_color: Optional[str] = None
    pattern: Optional[str] = None
    material: Optional[str] = None
    style: list[str] = Field(default_factory=list)
    season: list[str] = Field(default_factory=list)
    formality: Optional[str] = None
    fit: Optional[str] = None


class ItemBase(BaseModel):
    """Base item fields."""

    type: str = Field(default="unknown", max_length=50)  # Default to unknown, AI will detect
    subtype: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[Decimal] = Field(None, ge=0)
    favorite: bool = False


class ItemCreate(ItemBase):
    """Schema for creating an item (tags set by AI or manually)."""

    tags: Optional[ItemTags] = None
    colors: Optional[list[str]] = None
    primary_color: Optional[str] = None


class ItemUpdate(BaseModel):
    """Schema for updating an item."""

    type: Optional[str] = Field(None, min_length=1, max_length=50)
    subtype: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=100)
    brand: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[Decimal] = Field(None, ge=0)
    favorite: Optional[bool] = None
    tags: Optional[ItemTags] = None
    colors: Optional[list[str]] = None
    primary_color: Optional[str] = None


class ItemResponse(ItemBase):
    """Item response schema."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    image_path: str
    thumbnail_path: Optional[str] = None
    medium_path: Optional[str] = None
    tags: dict = Field(default_factory=dict)
    colors: list[str] = Field(default_factory=list)
    primary_color: Optional[str] = None
    pattern: Optional[str] = None
    material: Optional[str] = None
    style: list[str] = Field(default_factory=list)
    formality: Optional[str] = None
    season: list[str] = Field(default_factory=list)
    status: str
    ai_processed: bool = False
    ai_confidence: Optional[Decimal] = None
    ai_description: Optional[str] = None
    wear_count: int = 0
    last_worn_at: Optional[date] = None
    last_suggested_at: Optional[date] = None
    suggestion_count: int = 0
    acceptance_count: int = 0
    is_archived: bool = False
    archived_at: Optional[datetime] = None
    archive_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @computed_field
    @property
    def image_url(self) -> str:
        """Signed URL for the full-size image."""
        return sign_image_url(self.image_path)

    @computed_field
    @property
    def thumbnail_url(self) -> Optional[str]:
        """Signed URL for the thumbnail image."""
        if self.thumbnail_path:
            return sign_image_url(self.thumbnail_path)
        return None

    @computed_field
    @property
    def medium_url(self) -> Optional[str]:
        """Signed URL for the medium-size image."""
        if self.medium_path:
            return sign_image_url(self.medium_path)
        return None


class ItemListResponse(BaseModel):
    """Paginated item list response."""

    items: list[ItemResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class ItemFilter(BaseModel):
    """Filter parameters for item listing."""

    type: Optional[str] = None
    subtype: Optional[str] = None
    colors: Optional[list[str]] = None
    status: Optional[str] = None
    favorite: Optional[bool] = None
    is_archived: bool = False
    search: Optional[str] = None


class LogWearRequest(BaseModel):
    """Request to log an item as worn."""

    worn_at: date = Field(default_factory=date.today)
    occasion: Optional[str] = None
    notes: Optional[str] = None


class ArchiveRequest(BaseModel):
    """Request to archive an item."""

    reason: Optional[str] = Field(None, max_length=50)


class BulkUploadResult(BaseModel):
    """Result for a single item in bulk upload."""

    filename: str
    success: bool
    item: Optional[ItemResponse] = None
    error: Optional[str] = None


class BulkUploadResponse(BaseModel):
    """Response for bulk upload operation."""

    total: int
    successful: int
    failed: int
    results: list[BulkUploadResult]


class BulkFilters(BaseModel):
    """Filters for bulk operations when using select_all."""

    type: Optional[str] = None
    search: Optional[str] = None
    is_archived: Optional[bool] = None


class BulkDeleteRequest(BaseModel):
    """Request for bulk delete operation.

    Either provide item_ids for explicit selection,
    or use select_all=True with optional excluded_ids and filters.
    """

    # Explicit selection
    item_ids: Optional[list[UUID]] = None

    # Select all with exceptions
    select_all: bool = False
    excluded_ids: Optional[list[UUID]] = None
    filters: Optional[BulkFilters] = None

    def model_post_init(self, __context):
        """Validate that either item_ids or select_all is provided."""
        if not self.select_all and not self.item_ids:
            raise ValueError("Either item_ids or select_all=True must be provided")
        if self.select_all and self.item_ids:
            raise ValueError("Cannot use both item_ids and select_all")


class BulkDeleteResponse(BaseModel):
    """Response for bulk delete operation."""

    deleted: int
    failed: int
    errors: list[str] = Field(default_factory=list)


class BulkAnalyzeRequest(BaseModel):
    """Request for bulk re-analyze operation.

    Either provide item_ids for explicit selection,
    or use select_all=True with optional excluded_ids and filters.
    """

    # Explicit selection
    item_ids: Optional[list[UUID]] = None

    # Select all with exceptions
    select_all: bool = False
    excluded_ids: Optional[list[UUID]] = None
    filters: Optional[BulkFilters] = None

    def model_post_init(self, __context):
        """Validate that either item_ids or select_all is provided."""
        if not self.select_all and not self.item_ids:
            raise ValueError("Either item_ids or select_all=True must be provided")
        if self.select_all and self.item_ids:
            raise ValueError("Cannot use both item_ids and select_all")


class BulkAnalyzeResponse(BaseModel):
    """Response for bulk re-analyze operation."""

    queued: int
    failed: int
    errors: list[str] = Field(default_factory=list)
