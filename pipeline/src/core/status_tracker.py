"""
Status tracking for pipeline execution.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import asyncio
import json
from pathlib import Path


class PipelineStatus(Enum):
    """Pipeline execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StatusTracker:
    """
    Tracks pipeline execution status and progress.
    
    Stores status information in memory and optionally persists to disk.
    """
    
    def __init__(self, persist_path: Optional[Path] = None):
        """
        Initialize status tracker.
        
        Args:
            persist_path: Optional path to persist status data
        """
        self.persist_path = persist_path
        self.executions: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
    
    async def create_execution(self, execution_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new pipeline execution tracking entry.
        
        Args:
            execution_id: Unique execution identifier
            input_data: Initial input data
            
        Returns:
            Execution status dictionary
        """
        async with self._lock:
            execution = {
                "execution_id": execution_id,
                "status": PipelineStatus.PENDING.value,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "stages": [],
                "current_stage": None,
                "input_summary": self._summarize_data(input_data),
                "errors": [],
                "progress": 0
            }
            self.executions[execution_id] = execution
            await self._persist()
            return execution
    
    async def update_stage(
        self,
        execution_id: str,
        stage_name: str,
        status: str,
        result: Optional[Dict[str, Any]] = None,
        error: Optional[Dict[str, Any]] = None
    ):
        """
        Update status for a specific pipeline stage.
        
        Args:
            execution_id: Execution identifier
            stage_name: Name of the stage
            status: Stage status (running, completed, failed)
            result: Optional stage result data
            error: Optional error information
        """
        async with self._lock:
            if execution_id not in self.executions:
                return
            
            execution = self.executions[execution_id]
            
            # Update or add stage info
            stage_info = {
                "stage": stage_name,
                "status": status,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if result:
                stage_info["result_summary"] = self._summarize_data(result)
                if "_metadata" in result:
                    stage_info["metadata"] = result["_metadata"]
            
            if error:
                stage_info["error"] = error
                execution["errors"].append(error)
            
            # Find existing stage or append new
            existing_idx = next(
                (i for i, s in enumerate(execution["stages"]) if s["stage"] == stage_name),
                None
            )
            
            if existing_idx is not None:
                execution["stages"][existing_idx] = stage_info
            else:
                execution["stages"].append(stage_info)
            
            execution["current_stage"] = stage_name
            execution["updated_at"] = datetime.utcnow().isoformat()
            
            await self._persist()
    
    async def update_execution_status(
        self,
        execution_id: str,
        status: PipelineStatus,
        progress: Optional[int] = None
    ):
        """
        Update overall execution status.
        
        Args:
            execution_id: Execution identifier
            status: Pipeline status
            progress: Optional progress percentage (0-100)
        """
        async with self._lock:
            if execution_id not in self.executions:
                return
            
            execution = self.executions[execution_id]
            execution["status"] = status.value
            execution["updated_at"] = datetime.utcnow().isoformat()
            
            if progress is not None:
                execution["progress"] = progress
            
            if status == PipelineStatus.COMPLETED:
                execution["completed_at"] = datetime.utcnow().isoformat()
                execution["progress"] = 100
            
            await self._persist()
    
    async def get_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get execution status.
        
        Args:
            execution_id: Execution identifier
            
        Returns:
            Execution status dictionary or None if not found
        """
        async with self._lock:
            return self.executions.get(execution_id)
    
    async def list_executions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        List all executions.
        
        Args:
            limit: Maximum number of executions to return
            
        Returns:
            List of execution status dictionaries
        """
        async with self._lock:
            executions = list(self.executions.values())
            # Sort by created_at descending
            executions.sort(key=lambda x: x["created_at"], reverse=True)
            return executions[:limit]
    
    def _summarize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a summary of data without full content."""
        summary = {}
        for key, value in data.items():
            if key.startswith("_"):
                continue
            if isinstance(value, str) and len(value) > 100:
                summary[key] = f"{value[:100]}... (truncated)"
            elif isinstance(value, (list, dict)):
                summary[key] = f"<{type(value).__name__} with {len(value)} items>"
            else:
                summary[key] = value
        return summary
    
    async def _persist(self):
        """Persist status data to disk if path is configured."""
        if self.persist_path:
            try:
                self.persist_path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.persist_path, 'w') as f:
                    json.dump(self.executions, f, indent=2)
            except Exception as e:
                # Log error but don't fail
                print(f"Warning: Failed to persist status: {e}")
