"""
Conversation memory management for chat sessions.

Provides functionality for:
- Session-based conversation memory
- Automatic memory persistence
- Conversation history tracking
- Memory retrieval for context
"""
from typing import Dict, List, Optional


class ConversationMemoryManager:
    """
    Manages conversation memory for chat sessions using simple dict storage.
    """
    
    def __init__(
        self,
        max_history: int = 12
    ):
        """
        Initialize conversation memory manager.
        
        Args:
            max_history: Maximum number of message pairs to keep in memory
        """
        self.max_history = max_history
        
        # Session-based memory storage: {session_id: [{role, content}, ...]}
        self._sessions: Dict[str, List[Dict[str, str]]] = {}
    
    def get_memory(self, session_id: str) -> List[Dict[str, str]]:
        """
        Get memory for a session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            List of message dicts with role and content
        """
        if session_id not in self._sessions:
            self._sessions[session_id] = []
        
        return self._sessions[session_id]
    
    def add_message(
        self,
        session_id: str,
        human_message: str,
        ai_message: str
    ):
        """
        Add a message exchange to session memory.
        
        Args:
            session_id: Unique session identifier
            human_message: User's message
            ai_message: AI's response
        """
        memory = self.get_memory(session_id)
        
        # Add messages
        memory.append({"role": "user", "content": human_message})
        memory.append({"role": "assistant", "content": ai_message})
        
        # Trim history if it exceeds max_history (counting message pairs)
        if len(memory) > self.max_history * 2:
            # Remove oldest pair
            self._sessions[session_id] = memory[-(self.max_history * 2):]
    
    def get_history(
        self,
        session_id: str,
        as_messages: bool = False
    ) -> List:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Unique session identifier
            as_messages: Unused parameter for compatibility
            
        Returns:
            List of conversation messages
        """
        return self.get_memory(session_id)
    
    def get_history_text(self, session_id: str) -> str:
        """
        Get conversation history as formatted text.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Formatted conversation history string
        """
        history = self.get_history(session_id)
        
        if not history:
            return ""
        
        lines = []
        for msg in history:
            role = msg["role"]
            content = msg["content"]
            
            if role == "user":
                lines.append(f"User: {content}")
            elif role == "assistant":
                lines.append(f"Assistant: {content}")
        
        return "\n\n".join(lines)
    
    def clear_session(self, session_id: str):
        """
        Clear memory for a session.
        
        Args:
            session_id: Unique session identifier
        """
        if session_id in self._sessions:
            memory = self._sessions[session_id]
            memory.clear()
    
    def delete_session(self, session_id: str):
        """
        Delete a session completely.
        
        Args:
            session_id: Unique session identifier
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
    
    def get_session_count(self) -> int:
        """
        Get number of active sessions.
        
        Returns:
            Number of sessions
        """
        return len(self._sessions)
    
    def get_session_ids(self) -> List[str]:
        """
        Get all active session IDs.
        
        Returns:
            List of session IDs
        """
        return list(self._sessions.keys())
    

    
    def get_context_for_llm(
        self,
        session_id: str,
        include_system: bool = True,
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Get conversation history formatted for LLM input.
        
        Args:
            session_id: Unique session identifier
            include_system: Whether to include system prompt
            system_prompt: Optional system prompt to prepend
            
        Returns:
            List of message dicts ready for LLM
        """
        messages = []
        
        # Add system prompt if requested
        if include_system and system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        history = self.get_history(session_id)
        messages.extend(history)
        
        return messages


# Global memory manager instance
_memory_manager: Optional[ConversationMemoryManager] = None


def get_memory_manager() -> ConversationMemoryManager:
    """
    Get or create global memory manager instance.
    
    Returns:
        ConversationMemoryManager instance
    """
    global _memory_manager
    
    if _memory_manager is None:
        _memory_manager = ConversationMemoryManager()
    
    return _memory_manager


def add_to_memory(session_id: str, human_message: str, ai_message: str):
    """
    Add a message exchange to session memory.
    
    Args:
        session_id: Unique session identifier
        human_message: User's message
        ai_message: AI's response
    """
    manager = get_memory_manager()
    manager.add_message(session_id, human_message, ai_message)


def get_session_history(session_id: str) -> List[Dict[str, str]]:
    """
    Get conversation history for a session.
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        List of message dicts
    """
    manager = get_memory_manager()
    return manager.get_history(session_id)


def get_llm_context(
    session_id: str,
    system_prompt: Optional[str] = None
) -> List[Dict[str, str]]:
    """
    Get conversation history formatted for LLM input.
    
    Args:
        session_id: Unique session identifier
        system_prompt: Optional system prompt to prepend
        
    Returns:
        List of message dicts ready for LLM
    """
    manager = get_memory_manager()
    return manager.get_context_for_llm(
        session_id,
        include_system=system_prompt is not None,
        system_prompt=system_prompt
    )


def clear_session_memory(session_id: str):
    """
    Clear memory for a session.
    
    Args:
        session_id: Unique session identifier
    """
    manager = get_memory_manager()
    manager.clear_session(session_id)
