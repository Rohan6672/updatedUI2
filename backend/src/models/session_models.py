from datetime import datetime
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
import uuid

from pydantic import BaseModel,Field

class TrendResponse(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None


class TrendSendRequest(BaseModel):
    session_id: str
    user_id: str
    trend_query: str
    created_at: Optional[datetime] = None


class TrendItem(BaseModel):
    """
    Individual trend item matching frontend TrendCard interface.
    Uses camelCase for JSON output to match frontend expectations.
    """
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique trend identifier")
    trend_name: str = Field(..., alias="trendName", description="Name of the beauty trend")
    trend_description: str = Field(default="", alias="trendDescription", description="Detailed description of the trend")
    trend_summary: str = Field(default="", alias="trendSummary", description="Brief summary of the trend")
    category_associations: List[str] = Field(default_factory=list, alias="categoryAssociations", description="Sephora departments/categories")
    ingredients: List[str] = Field(default_factory=list, description="Key ingredients mentioned")
    product_features: List[str] = Field(default_factory=list, alias="productFeatures", description="Product features and attributes")
    keywords: List[str] = Field(default_factory=list, description="keywords")
    hashtags: List[str] = Field(default_factory=list, description="hashtags")
   


class TrendCategory(BaseModel):
    """All Sephora categories of trends."""
    makeup_trends: List[TrendItem] = Field(default_factory=list, alias="makeupTrends", description="Makeup trends")
    skincare_trends: List[TrendItem] = Field(default_factory=list, alias="skincareTrends", description="Skincare trends")
    hair_trends: List[TrendItem] = Field(default_factory=list, alias="hairTrends", description="Hair trends")
    tools_brushes_trends: List[TrendItem] = Field(default_factory=list, alias="toolsBrushesTrends", description="Tools & Brushes trends")
    mini_size_trends: List[TrendItem] = Field(default_factory=list, alias="miniSizeTrends", description="Mini Size trends")
    men_trends: List[TrendItem] = Field(default_factory=list, alias="menTrends", description="Men's grooming trends")
    gifts_trends: List[TrendItem] = Field(default_factory=list, alias="giftsTrends", description="Gifts trends")
    fragrance_trends: List[TrendItem] = Field(default_factory=list, alias="fragranceTrends", description="Fragrance trends")
    bath_body_trends: List[TrendItem] = Field(default_factory=list, alias="bathBodyTrends", description="Bath & Body trends")


class SephoraTrendsReport(BaseModel):
    """
    Complete trends report containing multiple trends across categories.
    """
    model_config = ConfigDict(populate_by_name=True)

    report_summary: str = Field(..., alias="reportSummary", description="Comprehensive summary of the overall beauty landscape")
    trends: TrendCategory = Field(..., description="Categorized trends")
    discovery_date: str = Field(default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%d"), alias="discoveryDate", description="Date trends were discovered")
    total_trends_found: int = Field(default=0, alias="totalTrendsFound", description="Total number of trends found")


    