"""
Quick fix script to update message.content column type from VARCHAR to TEXT
Run this directly in your PostgreSQL database
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from api.core.db import async_session


async def fix_message_content_column():
    """Fix message.content column type to TEXT."""
    print("🔧 Fixing message.content column type...")
    
    async with async_session() as session:
        try:
            # Check current column type
            check_query = text("""
                SELECT data_type, character_maximum_length 
                FROM information_schema.columns 
                WHERE table_name = 'message' AND column_name = 'content';
            """)
            result = await session.execute(check_query)
            current_type = result.fetchone()
            
            if current_type:
                print(f"📊 Current type: {current_type[0]}, max length: {current_type[1]}")
            
            # Alter column to TEXT
            alter_query = text("""
                ALTER TABLE message 
                ALTER COLUMN content TYPE TEXT;
            """)
            await session.execute(alter_query)
            await session.commit()
            
            print("✅ Successfully changed message.content to TEXT type!")
            
            # Verify the change
            result = await session.execute(check_query)
            new_type = result.fetchone()
            print(f"✨ New type: {new_type[0]}, max length: {new_type[1] or 'unlimited'}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            await session.rollback()
            raise


async def main():
    """Main function."""
    print("=" * 60)
    print("MESSAGE CONTENT COLUMN TYPE FIX")
    print("=" * 60)
    
    try:
        await fix_message_content_column()
        print("\n✅ Migration completed successfully!")
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
