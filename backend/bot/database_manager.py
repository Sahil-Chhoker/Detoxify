from backend.db.session import SUPABASE
import pickle
import base64
from datetime import datetime, timedelta


class DatabaseManager:
    def __init__(self):
        """Initialize Supabase client"""
        self.supabase = SUPABASE

    def init_db(self):
        """
        Initialize database tables if they don't exist
        Note: Run this once to create the table structure
        """
        # This should be run via Supabase interface or migration tool
        # Here's the SQL to create the tables:
        """
        -- Users table should already exist
        -- CREATE TABLE IF NOT EXISTS users (
        --     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        --     -- other user fields
        -- );
        
        CREATE TABLE IF NOT EXISTS sessions (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            cookies TEXT NOT NULL,
            user_agent TEXT,
            last_used TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            is_valid BOOLEAN DEFAULT TRUE,
            CONSTRAINT fk_user
                FOREIGN KEY(user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        );
        
        -- Indexes for faster lookups
        CREATE INDEX IF NOT EXISTS idx_sessions_user_id 
        ON sessions(user_id);
        
        CREATE INDEX IF NOT EXISTS idx_sessions_last_used 
        ON sessions(last_used);
        """
        pass

    def get_user(self, user_id):
        """Get user details from users table"""
        try:
            response = (
                self.supabase.table("users").select("*").eq("id", user_id).execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error getting user: {str(e)}")
            return None

    def save_session(self, user_id, cookies, user_agent=None):
        """Save browser session to Supabase"""
        try:
            # First verify user exists
            user = self.get_user(user_id)
            if not user:
                print(f"User {user_id} not found")
                return False

            # Convert cookies to base64 string
            cookies_str = base64.b64encode(pickle.dumps(cookies)).decode("utf-8")

            # Check if session exists
            response = (
                self.supabase.table("sessions")
                .select("id")
                .eq("user_id", user_id)
                .execute()
            )

            if response.data:
                # Update existing session
                self.supabase.table("sessions").update(
                    {
                        "cookies": cookies_str,
                        "user_agent": user_agent,
                        "last_used": datetime.utcnow().isoformat(),
                        "is_valid": True,
                    }
                ).eq("user_id", user_id).execute()
            else:
                # Insert new session
                self.supabase.table("sessions").insert(
                    {
                        "user_id": user_id,
                        "cookies": cookies_str,
                        "user_agent": user_agent,
                    }
                ).execute()

            return True
        except Exception as e:
            print(f"Error saving session to database: {str(e)}")
            return False

    def load_session(self, user_id):
        """Load browser session from Supabase"""
        try:
            # First verify user exists
            user = self.get_user(user_id)
            if not user:
                print(f"User {user_id} not found")
                return None, None

            response = (
                self.supabase.table("sessions")
                .select("*")
                .eq("user_id", user_id)
                .eq("is_valid", True)
                .execute()
            )

            if response.data:
                session_data = response.data[0]
                # Convert cookies from base64 string back to object
                cookies = pickle.loads(base64.b64decode(session_data["cookies"]))
                return cookies, session_data["user_agent"]
            return None, None
        except Exception as e:
            print(f"Error loading session from database: {str(e)}")
            return None, None

    def invalidate_session(self, user_id):
        """Mark a session as invalid"""
        try:
            # First verify user exists
            user = self.get_user(user_id)
            if not user:
                print(f"User {user_id} not found")
                return False

            self.supabase.table("sessions").update({"is_valid": False}).eq(
                "user_id", user_id
            ).execute()
            return True
        except Exception as e:
            print(f"Error invalidating session: {str(e)}")
            return False

    def cleanup_old_sessions(self, days=30):
        """Clean up old invalid sessions"""
        try:
            cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            self.supabase.table("sessions").delete().lt("last_used", cutoff_date).eq(
                "is_valid", False
            ).execute()
            return True
        except Exception as e:
            print(f"Error cleaning up old sessions: {str(e)}")
            return False
