from pymongo import MongoClient
from datetime import datetime, timezone
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = "nemi_wealth"
COLLECTION_NAME = "agent_conversations"

def get_collection():
    client = MongoClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    return db[COLLECTION_NAME]


def save_conversation(
    user_id: str,
    user_message: str,
    agent_response: str,
    session_id: str = None
) -> str:
    """
    Save a user message and agent response to MongoDB.
    Returns the session_id so it can be reused in the same conversation.
    """
    collection = get_collection()

    if session_id is None:
        session_id = str(uuid.uuid4())

    now = datetime.now(timezone.utc).isoformat()

    existing = collection.find_one({"session_id": session_id})

    if existing:
        collection.update_one(
            {"session_id": session_id},
            {
                "$push": {
                    "messages": {
                        "$each": [
                            {
                                "role": "user",
                                "content": user_message,
                                "timestamp": now
                            },
                            {
                                "role": "agent",
                                "content": agent_response,
                                "timestamp": now
                            }
                        ]
                    }
                },
                "$set": {"updated_at": now}
            }
        )
    else:
        collection.insert_one({
            "session_id": session_id,
            "user_id": user_id,
            "agent": "insurance_coverage_gap_analyzer",
            "created_at": now,
            "updated_at": now,
            "messages": [
                {
                    "role": "user",
                    "content": user_message,
                    "timestamp": now
                },
                {
                    "role": "agent",
                    "content": agent_response,
                    "timestamp": now
                }
            ]
        })

    return session_id


def load_conversation_history(session_id: str) -> list:
    """
    Load all messages for a given session.
    Returns a list of messages or empty list if session not found.
    """
    collection = get_collection()
    doc = collection.find_one({"session_id": session_id})
    if doc:
        return doc.get("messages", [])
    return []


def get_user_sessions(user_id: str) -> list:
    """
    Get all sessions for a given user.
    Returns list of session summaries.
    """
    collection = get_collection()
    sessions = collection.find(
        {"user_id": user_id},
        {"session_id": 1, "created_at": 1, "updated_at": 1, "_id": 0}
    ).sort("updated_at", -1)
    return list(sessions)