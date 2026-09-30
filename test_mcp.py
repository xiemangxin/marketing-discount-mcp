"""Real stdio protocol integration test."""
import asyncio
from pathlib import Path
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    params=StdioServerParameters(command=sys.executable,args=[str(Path(__file__).with_name('server.py'))])
    async with stdio_client(params) as (read,write):
        async with ClientSession(read,write) as session:
            await session.initialize()
            listing=await session.list_tools()
            assert {t.name for t in listing.tools} == {'calculate_discount_range','convert_discount'}
            result=await session.call_tool('calculate_discount_range', {'products':[{'id':'A','name':'香水','original_price':'1000','sale_price':'790'}]})
            assert not result.isError, result
            assert '21' in str(result)
            bad=await session.call_tool('calculate_discount_range', {'products':[{'id':'A','name':'錯價','original_price':'0','sale_price':'790'}]})
            assert bad.isError
            conversion=await session.call_tool('convert_discount', {'value':'8','input_type':'zhe'})
            assert not conversion.isError and '20' in str(conversion)
    print('PASS: MCP initialize, tools/list, tools/call, error response, conversion')

if __name__=='__main__': asyncio.run(main())
