from typing import Union
from datetime import datetime, timedelta
from fyodorov_utils.config.supabase import get_supabase
from fyodorov_llm_agents.tools.tool import Tool as ToolModel

class BaseModel():
    id: str = None

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def from_dict(self, data):
        for field in self.__table__.columns:
            if field.name in data:
                setattr(self, field.name, data[field.name])

class Base(BaseModel):
    table: str = 'ERROR: table not set'
    base_object: BaseModel = BaseModel()

    @staticmethod    
    def create_in_db(access_token: str) -> str:
        try:
            supabase = get_supabase(access_token)
            result = supabase.table(self.table).insert(self.base_object.to_dict()).execute()
            self.base_object.id = result.data[0]['id']
            return self.base_object.id
        except Exception as e:
            print('Error creating object in table', self.table, str(e))
            raise e

    @staticmethod
    def update_in_db(access_token: str, id: str) -> dict:
        if not id:
            raise ValueError('ID is required to update in table', self.table)
        try:
            supabase = get_supabase(access_token)
            result = supabase.table(self.table).update(self.base_object).eq('id', id).execute()
            return result.data[0]
        except Exception as e:
            print('An error occurred while updating table', self.table, id, str(e))
            raise

    @staticmethod
    def delete_in_db(access_token: str, id: str) -> bool:
        if not id:
            raise ValueError('ID is required to delete from table', self.table)
        try:
            supabase = get_supabase(access_token)
            result = supabase.table(self.table).delete().eq('id', id).execute()
            return True
        except Exception as e:
            print('Error deleting from table', self.table, str(e))
            raise e

    @staticmethod
    def get_in_db(access_token: str, id: str) -> BaseModel:
        if not id:
            raise ValueError('ID is required to get from table', self.table)
        try:
            supabase = get_supabase(access_token)
            result = supabase.table(self.table).select('*').eq('id', id).limit(1).execute()
            self.base_object.from_dict(result.data[0])
            return self.base_object
        except Exception as e:
            print('Error fetching tool', str(e))
            raise e

    @staticmethod
    def get_all_in_db(access_token: str, limit: int = 10, created_at_lt: datetime = datetime.now()) -> [dict]:
        try:
            supabase = get_supabase(access_token)
            result = supabase.from_(self.table) \
                .select("*") \
                .limit(limit) \
                .lt('created_at', created_at_lt) \
                .order('created_at', desc=True) \
                .execute()
            tools = result.data
            return tools
        except Exception as e:
            print('Error fetching multiple objects from table', self.table, str(e))
            raise e