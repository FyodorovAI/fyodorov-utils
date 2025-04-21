from typing import Union
from datetime import datetime, timedelta
from fyodorov_utils.config.supabase import get_supabase
from fyodorov_llm_agents.tools.mcp_tool import MCPTool as ToolModel
from .base import Base

class Tool(Base):

    @staticmethod    
    def create_in_db(access_token: str, tool: ToolModel) -> str:
        try:
            supabase = get_supabase(access_token)
            result = supabase.table('mcp_tools').insert(tool.to_dict()).execute()
            tool_id = result.data[0]['id']
            return tool_id
        except Exception as e:
            print('Error creating tool', str(e))
            raise e

    @staticmethod
    def update_in_db(access_token: str, id: str, tool: dict) -> dict:
        if not id:
            raise ValueError('Tool ID is required')
        try:
            supabase = get_supabase(access_token)
            result = supabase.table('mcp_tools').update(tool).eq('id', id).execute()
            return result.data[0]
        except Exception as e:
            print('An error occurred while updating tool:', id, str(e))
            raise

    @staticmethod
    def delete_in_db(access_token: str, id: str) -> bool:
        if not id:
            raise ValueError('Tool ID is required')
        try:
            supabase = get_supabase(access_token)
            result = supabase.table('mcp_tools').delete().eq('id', id).execute()
            return True
        except Exception as e:
            print('Error deleting tool', str(e))
            raise e

    @staticmethod
    def get_in_db(access_token: str, id: str) -> ToolModel:
        if not id:
            raise ValueError('Tool ID is required')
        try:
            supabase = get_supabase(access_token)
            result = supabase.table('mcp_tools').select('*').eq('id', id).limit(1).execute()
            tool_dict = result.data[0]
            print('got tool from db', tool_dict)
            tool = ToolModel(**tool_dict)
            return tool
        except Exception as e:
            print('Error fetching tool', str(e))
            raise e

    @staticmethod
    def get_by_name_and_user_id(access_token: str, handle: str, user_id: str) -> ToolModel:
        if not handle:
            raise ValueError('Tool name is required')
        try:
            supabase = get_supabase(access_token)
            result = supabase.table('mcp_tools').select('*').eq('handle', handle).eq('user_id', user_id).limit(1).execute()
            if not result.data: # If no tools found for this user check for public tools with same name
                result = supabase.table('mcp_tools').select('*').eq('handle', handle).eq('public', True).limit(1).execute()
            if not result.data:
                print(f"No tool found with name {handle} and user_id {user_id}")
                return None
            tool_dict = result.data[0]
            tool_dict['handle'] = tool_dict['handle']
            tool_dict['description'] = tool_dict['description']
            print('got tool from db', tool_dict)
            tool = ToolModel(**tool_dict)
            return tool
        except Exception as e:
            print('Error fetching tool', str(e))
            raise e

    @staticmethod
    def get_all_in_db(access_token: str, limit: int = 10, created_at_lt: datetime = datetime.now()) -> [dict]:
        try:
            supabase = get_supabase(access_token)
            result = supabase.from_('mcp_tools') \
                .select("*") \
                .limit(limit) \
                .lt('created_at', created_at_lt) \
                .order('created_at', desc=True) \
                .execute()
            tools = result.data
            return tools
        except Exception as e:
            print('Error fetching tools', str(e))
            raise e