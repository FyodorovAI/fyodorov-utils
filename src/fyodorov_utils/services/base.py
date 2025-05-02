from datetime import datetime
from fyodorov_utils.config.supabase import get_supabase


class Model:
    id: str = None

    def to_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}

    def from_dict(self, data):
        for field in self.__table__.columns:
            if field.name in data:
                setattr(self, field.name, data[field.name])


class Base(Model):
    table: str = "ERROR: table not set"

    def create_in_db(self, access_token: str) -> str:
        try:
            supabase = get_supabase(access_token)
            result = supabase.table(self.table).insert(self.to_dict()).execute()
            self.id = result.data[0]["id"]
            return self.id
        except Exception as e:
            print("Error creating object in table", self.table, str(e))
            raise e

    def update_in_db(self, access_token: str, id: str) -> dict:
        if not id:
            raise ValueError("ID is required to update in table", self.table)
        try:
            self.id = id
            supabase = get_supabase(access_token)
            result = (
                supabase.table(self.table)
                .update(self.to_dict())
                .eq("id", self.id)
                .execute()
            )
            return result.data[0]
        except Exception as e:
            print("An error occurred while updating table", self.table, id, str(e))
            raise

    def delete_in_db(self, access_token: str, id: str) -> bool:
        if not id:
            raise ValueError("ID is required to delete from table", self.table)
        try:
            self.id = id
            supabase = get_supabase(access_token)
            supabase.table(self.table).delete().eq("id", self.id).execute()
            return True
        except Exception as e:
            print("Error deleting from table", self.table, str(e))
            raise e

    def get_in_db(self, access_token: str, id: str) -> Model:
        if not id:
            raise ValueError("ID is required to get from table", self.table)
        try:
            self.id = id
            supabase = get_supabase(access_token)
            result = (
                supabase.table(self.table)
                .select("*")
                .eq("id", self.id)
                .limit(1)
                .execute()
            )
            self.from_dict(result.data[0])
            return self.base_object
        except Exception as e:
            print("Error fetching tool", str(e))
            raise e

    def get_all_in_db(
        self,
        access_token: str,
        limit: int = 10,
        created_at_lt: datetime = datetime.now(),
    ) -> [dict]:
        try:
            supabase = get_supabase(access_token)
            result = (
                supabase.from_(self.table)
                .select("*")
                .limit(limit)
                .lt("created_at", created_at_lt)
                .order("created_at", desc=True)
                .execute()
            )
            tools = result.data
            return tools
        except Exception as e:
            print("Error fetching multiple objects from table", self.table, str(e))
            raise e
