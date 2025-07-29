"""
Queue Router für ChiliView
Verwaltet die Processing Queue und bietet Status-Informationen
"""

import logging
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_database
from database.models import User, Project
from auth.auth_handler import get_current_user
from services.processing_queue import get_processing_queue, ProcessingQueueManager

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/status")
async def get_queue_status(
    current_user: User = Depends(get_current_user),
    queue_manager: ProcessingQueueManager = Depends(get_processing_queue)
):
    """Ruft allgemeine Queue-Informationen ab"""
    try:
        queue_info = await queue_manager.get_queue_info()
        
        return {
            "queue_size": queue_info["queue_size"],
            "running_jobs": queue_info["running_jobs"],
            "max_concurrent_jobs": queue_info["max_concurrent_jobs"],
            "max_queue_size": queue_info["max_queue_size"],
            "server_load": "normal" if queue_info["queue_size"] < 10 else "high"
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Queue-Status: {e}")
        raise HTTPException(status_code=500, detail="Fehler beim Abrufen des Queue-Status")

@router.get("/task/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
    queue_manager: ProcessingQueueManager = Depends(get_processing_queue)
):
    """Ruft den Status einer spezifischen Task ab"""
    try:
        task_status = await queue_manager.get_task_status(task_id)
        
        if not task_status:
            raise HTTPException(status_code=404, detail="Task nicht gefunden")
            
        return task_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Task-Status: {e}")
        raise HTTPException(status_code=500, detail="Fehler beim Abrufen des Task-Status")

@router.delete("/task/{task_id}")
async def cancel_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    queue_manager: ProcessingQueueManager = Depends(get_processing_queue)
):
    """Bricht eine Task ab (nur vom Besitzer)"""
    try:
        success = await queue_manager.cancel_task(task_id, current_user.id)
        
        if not success:
            raise HTTPException(
                status_code=400, 
                detail="Task konnte nicht abgebrochen werden (nicht gefunden oder bereits gestartet)"
            )
            
        return {"message": "Task erfolgreich abgebrochen", "task_id": task_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Abbrechen der Task: {e}")
        raise HTTPException(status_code=500, detail="Fehler beim Abbrechen der Task")

@router.get("/my-tasks")
async def get_my_tasks(
    current_user: User = Depends(get_current_user),
    queue_manager: ProcessingQueueManager = Depends(get_processing_queue),
    db: Session = Depends(get_database)
):
    """Ruft alle Tasks des aktuellen Benutzers ab"""
    try:
        # Alle Projekte des Benutzers laden
        user_projects = db.query(Project).filter(Project.user_id == current_user.id).all()
        project_ids = [p.id for p in user_projects]
        
        # Queue-Info abrufen
        queue_info = await queue_manager.get_queue_info()
        
        # Tasks des Benutzers filtern
        user_tasks = []
        
        # Wartende Tasks
        for task_info in queue_info.get("next_tasks", []):
            if task_info["project_id"] in project_ids:
                task_status = await queue_manager.get_task_status(task_info["task_id"])
                if task_status:
                    user_tasks.append({
                        **task_status,
                        "category": "queued"
                    })
        
        # Laufende Tasks (vereinfacht - in echter Implementierung würde man alle durchgehen)
        for task_id in queue_manager.running_tasks:
            task = queue_manager.running_tasks[task_id]
            if task.project_id in project_ids:
                user_tasks.append({
                    **queue_manager._task_to_dict(task),
                    "category": "running"
                })
        
        # Kürzlich abgeschlossene Tasks (letzte 10)
        recent_completed = []
        for task_id, task in list(queue_manager.completed_tasks.items())[-10:]:
            if task.project_id in project_ids:
                recent_completed.append({
                    **queue_manager._task_to_dict(task),
                    "category": "completed"
                })
        
        user_tasks.extend(recent_completed)
        
        # Nach Erstellungszeit sortieren (neueste zuerst)
        user_tasks.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return {
            "tasks": user_tasks,
            "total_count": len(user_tasks),
            "queue_position_info": f"Aktuell {queue_info['running_jobs']} von {queue_info['max_concurrent_jobs']} Slots belegt"
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Benutzer-Tasks: {e}")
        raise HTTPException(status_code=500, detail="Fehler beim Abrufen der Tasks")

@router.get("/admin/overview")
async def get_admin_queue_overview(
    current_user: User = Depends(get_current_user),
    queue_manager: ProcessingQueueManager = Depends(get_processing_queue)
):
    """Admin-Übersicht über die gesamte Queue (nur für Admins)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Nur für Administratoren")
        
    try:
        queue_info = await queue_manager.get_queue_info()
        
        # Detaillierte Statistiken
        running_tasks_details = []
        for task_id, task in queue_manager.running_tasks.items():
            running_tasks_details.append({
                "task_id": task_id,
                "project_id": task.project_id,
                "reseller_id": task.reseller_id,
                "user_id": task.user_id,
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "progress": task.progress
            })
        
        # Queue-Statistiken
        queue_stats = {
            "total_in_queue": len(queue_manager.queue),
            "currently_running": len(queue_manager.running_tasks),
            "completed_today": len([
                t for t in queue_manager.completed_tasks.values()
                if t.completed_at and t.completed_at.date() == queue_manager.completed_tasks[list(queue_manager.completed_tasks.keys())[0]].completed_at.date()
            ]) if queue_manager.completed_tasks else 0
        }
        
        return {
            "queue_info": queue_info,
            "running_tasks": running_tasks_details,
            "statistics": queue_stats,
            "system_status": {
                "queue_health": "healthy" if len(queue_manager.queue) < queue_manager.max_queue_size * 0.8 else "warning",
                "processing_capacity": f"{len(queue_manager.running_tasks)}/{queue_manager.max_concurrent_jobs}"
            }
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Admin-Queue-Übersicht: {e}")
        raise HTTPException(status_code=500, detail="Fehler beim Abrufen der Übersicht")

@router.post("/admin/configure")
async def configure_queue(
    max_concurrent_jobs: Optional[int] = None,
    max_queue_size: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    queue_manager: ProcessingQueueManager = Depends(get_processing_queue)
):
    """Konfiguriert Queue-Parameter (nur für Admins)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Nur für Administratoren")
        
    try:
        changes = {}
        
        if max_concurrent_jobs is not None:
            if 1 <= max_concurrent_jobs <= 10:
                queue_manager.max_concurrent_jobs = max_concurrent_jobs
                changes["max_concurrent_jobs"] = max_concurrent_jobs
            else:
                raise HTTPException(status_code=400, detail="max_concurrent_jobs muss zwischen 1 und 10 liegen")
        
        if max_queue_size is not None:
            if 10 <= max_queue_size <= 200:
                queue_manager.max_queue_size = max_queue_size
                changes["max_queue_size"] = max_queue_size
            else:
                raise HTTPException(status_code=400, detail="max_queue_size muss zwischen 10 und 200 liegen")
        
        if changes:
            await queue_manager.save_queue_state()
            logger.info(f"Queue-Konfiguration geändert von Admin {current_user.username}: {changes}")
        
        return {
            "message": "Queue-Konfiguration aktualisiert",
            "changes": changes,
            "current_config": {
                "max_concurrent_jobs": queue_manager.max_concurrent_jobs,
                "max_queue_size": queue_manager.max_queue_size
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Fehler beim Konfigurieren der Queue: {e}")
        raise HTTPException(status_code=500, detail="Fehler beim Konfigurieren der Queue")