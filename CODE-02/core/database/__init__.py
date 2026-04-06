"""
============================================================
DATABASE MODULE - Enhanced Memory Storage
============================================================
SQLite + Vector DB for semantic memory storage
"""

import sqlite3
import json
import os
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import threading
import hashlib


@dataclass
class MemoryEntry:
    id: int
    key: str
    value: str
    entry_type: str  # conversation, action, knowledge, preference
    tags: List[str]
    importance: float  # 0-1
    created_at: str
    accessed_at: str
    access_count: int


class VectorStore:
    """
    Simple vector store using SQLite with TF-IDF-like similarity
    For production, consider using ChromaDB or FAISS
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_schema()
    
    def _init_schema(self):
        """Initialize database schema"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS vectors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                embedding BLOB,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_content ON vectors(content)
        """)
        
        self.conn.commit()
    
    def add(self, content: str, metadata: Dict = None) -> int:
        """Add content to vector store"""
        cursor = self.conn.execute(
            "INSERT INTO vectors (content, metadata) VALUES (?, ?)",
            (content, json.dumps(metadata) if metadata else None)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Search by keyword similarity"""
        # Simple keyword matching for now
        keywords = query.lower().split()
        
        cursor = self.conn.execute(
            "SELECT id, content, metadata, created_at FROM vectors ORDER BY id DESC"
        )
        
        results = []
        for row in cursor:
            content_lower = row[1].lower()
            
            # Count keyword matches
            score = sum(1 for kw in keywords if kw in content_lower)
            
            if score > 0:
                results.append({
                    "id": row[0],
                    "content": row[1],
                    "metadata": json.loads(row[2]) if row[2] else {},
                    "created_at": row[3],
                    "score": score / len(keywords)
                })
        
        # Sort by score and limit
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    
    def get(self, id: int) -> Optional[Dict]:
        """Get entry by ID"""
        cursor = self.conn.execute(
            "SELECT id, content, metadata, created_at FROM vectors WHERE id = ?",
            (id,)
        )
        row = cursor.fetchone()
        
        if row:
            return {
                "id": row[0],
                "content": row[1],
                "metadata": json.loads(row[2]) if row[2] else {},
                "created_at": row[3]
            }
        return None
    
    def delete(self, id: int) -> bool:
        """Delete entry by ID"""
        self.conn.execute("DELETE FROM vectors WHERE id = ?", (id,))
        self.conn.commit()
        return self.conn.total_changes > 0
    
    def count(self) -> int:
        """Get total count"""
        cursor = self.conn.execute("SELECT COUNT(*) FROM vectors")
        return cursor.fetchone()[0]
    
    def close(self):
        """Close database connection"""
        self.conn.close()


class KnowledgeGraph:
    """
    Simple knowledge graph for storing relationships
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_schema()
    
    def _init_schema(self):
        """Initialize KG schema"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                entity_type TEXT,
                properties TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_entity TEXT NOT NULL,
                to_entity TEXT NOT NULL,
                relationship_type TEXT,
                properties TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.conn.commit()
    
    def add_entity(self, name: str, entity_type: str = None, properties: Dict = None) -> int:
        """Add an entity"""
        cursor = self.conn.execute(
            """INSERT OR REPLACE INTO entities (name, entity_type, properties)
               VALUES (?, ?, ?)""",
            (name, entity_type, json.dumps(properties) if properties else None)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def add_relationship(
        self, 
        from_entity: str, 
        to_entity: str, 
        rel_type: str,
        properties: Dict = None
    ) -> int:
        """Add a relationship between entities"""
        cursor = self.conn.execute(
            """INSERT INTO relationships (from_entity, to_entity, relationship_type, properties)
               VALUES (?, ?, ?, ?)""",
            (from_entity, to_entity, rel_type, json.dumps(properties) if properties else None)
        )
        self.conn.commit()
        return cursor.lastrowid
    
    def get_entity(self, name: str) -> Optional[Dict]:
        """Get entity by name"""
        cursor = self.conn.execute(
            "SELECT * FROM entities WHERE name = ?", (name,)
        )
        row = cursor.fetchone()
        
        if row:
            return {
                "id": row[0],
                "name": row[1],
                "type": row[2],
                "properties": json.loads(row[3]) if row[3] else {},
                "created_at": row[4]
            }
        return None
    
    def get_related(self, entity: str, rel_type: str = None) -> List[Dict]:
        """Get entities related to given entity"""
        query = """
            SELECT r.*, e.name, e.entity_type 
            FROM relationships r
            JOIN entities e ON (
                (r.from_entity = ? AND r.to_entity = e.name) OR
                (r.to_entity = ? AND r.from_entity = e.name)
            )
        """
        params = [entity, entity]
        
        if rel_type:
            query += " WHERE r.relationship_type = ?"
            params.append(rel_type)
        
        cursor = self.conn.execute(query, params)
        
        results = []
        for row in cursor:
            results.append({
                "from": row[1],
                "to": row[2],
                "type": row[3],
                "properties": json.loads(row[4]) if row[4] else {},
                "entity_name": row[6],
                "entity_type": row[7]
            })
        
        return results
    
    def close(self):
        """Close connection"""
        self.conn.close()


class EnhancedMemory:
    """
    Enhanced memory system with:
    - SQLite storage
    - Vector search
    - Knowledge graph
    - Automatic summarization
    """
    
    def __init__(self, data_dir: str = "data/memory"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize stores
        self.vector_store = VectorStore(os.path.join(data_dir, "vectors.db"))
        self.knowledge_graph = KnowledgeGraph(os.path.join(data_dir, "knowledge.db"))
        
        # Initialize main memory table
        self.conn = sqlite3.connect(os.path.join(data_dir, "memory.db"), check_same_thread=False)
        self._init_memory_schema()
        
        # Semaphore for thread safety
        self.lock = threading.Lock()
        
        # Stats
        self.stats = {
            "total_memories": 0,
            "total_knowledge": 0,
            "total_vectors": 0
        }
        self._update_stats()
    
    def _init_memory_schema(self):
        """Initialize memory schema"""
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                entry_type TEXT DEFAULT 'general',
                tags TEXT,
                importance REAL DEFAULT 0.5,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                accessed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                access_count INTEGER DEFAULT 0
            )
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_key ON memories(key)
        """)
        
        self.conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_type ON memories(entry_type)
        """)
        
        self.conn.commit()
    
    def store(
        self,
        key: str,
        value: str,
        entry_type: str = "general",
        tags: List[str] = None,
        importance: float = 0.5
    ) -> int:
        """Store a memory"""
        with self.lock:
            tags_str = json.dumps(tags) if tags else "[]"
            
            cursor = self.conn.execute("""
                INSERT OR REPLACE INTO memories 
                (key, value, entry_type, tags, importance, accessed_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (key, value, entry_type, tags_str, importance))
            
            self.conn.commit()
            
            # Also store in vector store for search
            vector_id = self.vector_store.add(
                f"{key}: {value}",
                {"key": key, "type": entry_type, "importance": importance}
            )
            
            self._update_stats()
            
            return cursor.lastrowid
    
    def recall(self, key: str) -> Optional[str]:
        """Recall a specific memory"""
        with self.lock:
            cursor = self.conn.execute(
                """UPDATE memories SET access_count = access_count + 1, 
                   accessed_at = CURRENT_TIMESTAMP WHERE key = ?""",
                (key,)
            )
            self.conn.commit()
            
            cursor = self.conn.execute(
                "SELECT value FROM memories WHERE key = ?", (key,)
            )
            row = cursor.fetchone()
            
            return row[0] if row else None
    
    def search(self, query: str, limit: int = 10) -> List[MemoryEntry]:
        """Search memories semantically"""
        # Search vector store
        vector_results = self.vector_store.search(query, limit)
        
        # Also search by keyword
        with self.lock:
            cursor = self.conn.execute(
                """SELECT * FROM memories 
                   WHERE key LIKE ? OR value LIKE ?
                   ORDER BY importance DESC, access_count DESC
                   LIMIT ?""",
                (f"%{query}%", f"%{query}%", limit)
            )
            
            sql_results = []
            for row in cursor:
                sql_results.append(MemoryEntry(
                    id=row[0],
                    key=row[1],
                    value=row[2],
                    entry_type=row[3],
                    tags=json.loads(row[4]) if row[4] else [],
                    importance=row[5],
                    created_at=row[6],
                    accessed_at=row[7],
                    access_count=row[8]
                ))
        
        # Merge results
        seen_ids = set()
        merged = []
        
        for r in vector_results:
            if r["id"] not in seen_ids:
                seen_ids.add(r["id"])
                merged.append(r)
        
        for m in sql_results:
            if m.id not in seen_ids:
                seen_ids.add(m.id)
                merged.append(m)
        
        return merged[:limit]
    
    def store_knowledge(
        self,
        subject: str,
        predicate: str,
        object: str,
        properties: Dict = None
    ):
        """Store a knowledge triple (subject, predicate, object)"""
        # Add entities
        self.knowledge_graph.add_entity(subject)
        self.knowledge_graph.add_entity(object)
        
        # Add relationship
        self.knowledge_graph.add_relationship(
            subject, object, predicate, properties
        )
        
        # Also store in vector and regular memory
        self.store(
            f"{subject} {predicate}",
            object,
            entry_type="knowledge",
            tags=[subject, predicate]
        )
        
        self._update_stats()
    
    def recall_knowledge(self, subject: str, predicate: str = None) -> List[Dict]:
        """Recall knowledge about a subject"""
        return self.knowledge_graph.get_related(subject, predicate)
    
    def store_conversation(
        self,
        role: str,
        content: str,
        context: str = None
    ):
        """Store a conversation turn"""
        key = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.store(
            key,
            content,
            entry_type="conversation",
            tags=[role, "dialogue"],
            importance=0.3
        )
        
        # Also add to vector store
        self.vector_store.add(
            f"{role}: {content}",
            {"role": role, "context": context, "timestamp": datetime.now().isoformat()}
        )
        
        self._update_stats()
    
    def get_recent_conversations(self, limit: int = 20) -> List[Dict]:
        """Get recent conversations"""
        with self.lock:
            cursor = self.conn.execute(
                """SELECT key, value, tags, created_at FROM memories 
                   WHERE entry_type = 'conversation'
                   ORDER BY created_at DESC LIMIT ?""",
                (limit,)
            )
            
            return [
                {
                    "key": row[0],
                    "content": row[1],
                    "role": json.loads(row[2])[0] if row[2] else "unknown",
                    "timestamp": row[3]
                }
                for row in cursor
            ]
    
    def learn_from_action(
        self,
        action: str,
        success: bool,
        result: str,
        error: str = None
    ):
        """Store learned information from an action"""
        key = hashlib.md5(action.encode()).hexdigest()[:12]
        
        self.store(
            f"action_{key}",
            json.dumps({
                "action": action,
                "success": success,
                "result": result,
                "error": error,
                "timestamp": datetime.now().isoformat()
            }),
            entry_type="action",
            tags=["learned", "action"],
            importance=0.8 if success else 0.9  # Failures are more important
        )
    
    def get_action_history(self, limit: int = 50) -> List[Dict]:
        """Get history of actions"""
        with self.lock:
            cursor = self.conn.execute(
                """SELECT value FROM memories 
                   WHERE entry_type = 'action'
                   ORDER BY created_at DESC LIMIT ?""",
                (limit,)
            )
            
            return [json.loads(row[0]) for row in cursor]
    
    def _update_stats(self):
        """Update memory statistics"""
        cursor = self.conn.execute("SELECT COUNT(*) FROM memories")
        self.stats["total_memories"] = cursor.fetchone()[0]
        
        self.stats["total_vectors"] = self.vector_store.count()
        
        cursor = self.conn.execute("SELECT COUNT(*) FROM entities")
        self.stats["total_knowledge"] = cursor.fetchone()[0]
    
    def get_stats(self) -> Dict:
        """Get memory statistics"""
        self._update_stats()
        return self.stats.copy()
    
    def cleanup(self, days: int = 30, min_importance: float = 0.3):
        """Clean up old, low-importance memories"""
        with self.lock:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            
            self.conn.execute(
                """DELETE FROM memories 
                   WHERE created_at < ? AND importance < ?""",
                (cutoff, min_importance)
            )
            self.conn.commit()
            
            self._update_stats()
    
    def close(self):
        """Close all connections"""
        self.conn.close()
        self.vector_store.close()
        self.knowledge_graph.close()
    
    def export(self, filepath: str):
        """Export all memory to JSON"""
        with self.lock:
            cursor = self.conn.execute("SELECT * FROM memories")
            
            memories = []
            for row in cursor:
                memories.append({
                    "id": row[0],
                    "key": row[1],
                    "value": row[2],
                    "type": row[3],
                    "tags": json.loads(row[4]) if row[4] else [],
                    "importance": row[5],
                    "created_at": row[6],
                    "accessed_at": row[7],
                    "access_count": row[8]
                })
        
        with open(filepath, "w") as f:
            json.dump(memories, f, indent=2)
    
    def import_memory(self, filepath: str):
        """Import memories from JSON"""
        with open(filepath, "r") as f:
            memories = json.load(f)
        
        for mem in memories:
            self.store(
                mem["key"],
                mem["value"],
                entry_type=mem.get("type", "general"),
                tags=mem.get("tags", []),
                importance=mem.get("importance", 0.5)
            )


# Singleton instance
_memory_instance: Optional[EnhancedMemory] = None

def get_enhanced_memory() -> EnhancedMemory:
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = EnhancedMemory()
    return _memory_instance
