from typing import Literal
from pydantic import BaseModel, ConfigDict, Field
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations
from calculator import calculate_discount_range as calculate, convert_discount as convert

mcp = FastMCP('Marketing Discount Calculator', instructions='繁體中文行銷折扣計算。折數越低優惠越大；省%越高優惠越大。禁止把指定商品擴寫成全館。不同優惠資格或幣別應分次呼叫。')

class Product(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    id: str = Field(description='唯一商品編號')
    name: str = Field(description='商品名稱')
    original_price: str = Field(description='原價，例如 "1000"，不含逗號、幣別；最多六位小數')
    sale_price: str = Field(description='已確認適用條件後的實付價，例如 "790"')

annotations = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)

@mcp.tool(annotations=annotations)
def calculate_discount_range(products: list[Product], currency: str = 'TWD', conditions: str = '') -> dict:
    """計算商品最低/最高折數、省%區間及保守行銷文案。所有商品必須同幣別、同資格條件；會員/滿額/輸碼條件寫入 conditions。不得將回饋或贈品當成現折。"""
    return calculate([p.model_dump() for p in products], currency, conditions)

@mcp.tool(annotations=annotations)
def convert_discount(value: str, input_type: Literal['zhe', 'percent_off']) -> dict:
    """折數與折扣百分比換算。例如 8 折=20% OFF；8 折不是 80% OFF。"""
    return convert(value, input_type)

if __name__ == '__main__':
    mcp.run(transport='stdio')
