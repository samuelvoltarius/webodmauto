"""
Processing Queue Service für WebODM-CLI
Verwaltet gleichzeitige Verarbeitungsanfragen mit parallelen WebODM-CLI Instanzen
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import json
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class QueueStatus(Enum):
    QUEUED = "queued"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class ProcessingTask:
    """Repräsentiert eine Verarbeitungsaufgabe in der Queue"""
    task_id: str
    project_id: int
    reseller_id: str
    user_id: int
    project_path: str
    images_path: str
    options: Dict
    priority: int = 0
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: QueueStatus = QueueStatus.QUEUED
    progress: int = 0
    error_message: Optional[str] = None
    instance_id: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class ProcessingQueueManager:
    """Verwaltet die WebODM-CLI Verarbeitungsqueue mit konfigurierbaren parallelen Instanzen"""
    
    def __init__(self, max_concurrent_jobs: int = None, max_queue_size: int = 50):
        # Konfigurierte Anzahl aus Umgebungsvariablen laden
        if max_concurrent_jobs is None:
            # Zuerst aus .env-Datei versuchen
            env_instances = os.getenv("MAX_WEBODM_INSTANCES")
            if env_instances and env_instances.isdigit():
                self.max_concurrent_jobs = int(env_instances)
            else:
                # Fallback: Automatische Erkennung basierend auf Hardware
                cpu_count = os.cpu_count() or 4
                self.max_concurrent_jobs = max(1, min(cpu_count // 2, 8))
        else:
            self.max_concurrent_jobs = max_concurrent_jobs
            
        self.max_queue_size = max_queue_size
        
        # Queue-Verwaltung
        self.queue: List[ProcessingTask] = []
        self.running_tasks: Dict[str, ProcessingTask] = {}
        self.completed_tasks: Dict[str, ProcessingTask] = {}
        
        # Locks für Thread-Sicherheit
        self.queue_lock = asyncio.Lock()
        self.running_lock = asyncio.Lock()
        
        # Queue-Worker
        self.worker_task = None
        self.is_running = False
        
        # Persistierung
        self.queue_file = Path("data/processing_queue.json")
        
    async def start(self):
        """Startet den Queue-Manager"""
        if self.is_running:
            return
            
        self.is_running = True
        await self.load_queue_state()
        
        # Worker-Task starten
        self.worker_task = asyncio.create_task(self._queue_worker())
        logger.info(f"Processing Queue Manager gestartet (max {self.max_concurrent_jobs} parallele WebODM-CLI Instanzen)")
        
    async def stop(self):
        """Stoppt den Queue-Manager"""
        self.is_running = False
        
        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass
                
        await self.save_queue_state()
        logger.info("Processing Queue Manager gestoppt")
        
    async def add_task(self, project_id: int, reseller_id: str, user_id: int,
                      project_path: str, images_path: str, options: Dict = None,
                      priority: int = 0) -> str:
        """
        Fügt eine neue Verarbeitungsaufgabe zur Queue hinzu
        
        Returns:
            task_id: Eindeutige Task-ID
        """
        async with self.queue_lock:
            # Queue-Größe prüfen
            if len(self.queue) >= self.max_queue_size:
                raise Exception(f"Queue ist voll (max {self.max_queue_size} Tasks)")
                
            # Task-ID generieren
            task_id = f"task_{project_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Task erstellen
            task = ProcessingTask(
                task_id=task_id,
                project_id=project_id,
                reseller_id=reseller_id,
                user_id=user_id,
                project_path=project_path,
                images_path=images_path,
                options=options or {},
                priority=priority
            )
            
            # Zur Queue hinzufügen (nach Priorität sortiert)
            self.queue.append(task)
            self.queue.sort(key=lambda t: (-t.priority, t.created_at))
            
            await self.save_queue_state()
            
            logger.info(f"Task {task_id} zur Queue hinzugefügt (Position: {len(self.queue)})")
            return task_id
            
    async def get_task_status(self, task_id: str) -> Optional[Dict]:
        """Ruft den Status einer Task ab"""
        # In laufenden Tasks suchen
        async with self.running_lock:
            if task_id in self.running_tasks:
                task = self.running_tasks[task_id]
                return self._task_to_dict(task)
                
        # In Queue suchen
        async with self.queue_lock:
            for i, task in enumerate(self.queue):
                if task.task_id == task_id:
                    return {
                        **self._task_to_dict(task),
                        "queue_position": i + 1,
                        "estimated_wait_time": self._estimate_wait_time(i)
                    }
                    
        # In abgeschlossenen Tasks suchen
        if task_id in self.completed_tasks:
            return self._task_to_dict(self.completed_tasks[task_id])
            
        return None
        
    async def cancel_task(self, task_id: str, user_id: int) -> bool:
        """Bricht eine Task ab (nur vom Besitzer)"""
        # In Queue suchen und entfernen
        async with self.queue_lock:
            for i, task in enumerate(self.queue):
                if task.task_id == task_id and task.user_id == user_id:
                    task.status = QueueStatus.CANCELLED
                    self.queue.pop(i)
                    self.completed_tasks[task_id] = task
                    await self.save_queue_state()
                    logger.info(f"Task {task_id} abgebrochen")
                    return True
                    
        # Laufende Tasks können nicht abgebrochen werden
        # (WebODM-CLI unterstützt kein graceful cancellation)
        return False
        
    async def get_queue_info(self) -> Dict:
        """Ruft Informationen über die Queue ab"""
        async with self.queue_lock:
            async with self.running_lock:
                return {
                    "queue_size": len(self.queue),
                    "running_jobs": len(self.running_tasks),
                    "max_concurrent_jobs": self.max_concurrent_jobs,
                    "max_queue_size": self.max_queue_size,
                    "next_tasks": [
                        {
                            "task_id": task.task_id,
                            "project_id": task.project_id,
                            "created_at": task.created_at.isoformat(),
                            "priority": task.priority
                        }
                        for task in self.queue[:5]  # Nächste 5 Tasks
                    ]
                }
                
    async def _queue_worker(self):
        """Worker-Loop für die Queue-Verarbeitung"""
        while self.is_running:
            try:
                # Prüfen ob neue Tasks gestartet werden können
                async with self.running_lock:
                    if len(self.running_tasks) >= self.max_concurrent_jobs:
                        await asyncio.sleep(5)
                        continue
                        
                # Nächste Task aus Queue holen
                next_task = None
                async with self.queue_lock:
                    if self.queue:
                        next_task = self.queue.pop(0)
                        
                if next_task:
                    # Task starten
                    await self._start_task(next_task)
                else:
                    # Keine Tasks in Queue, kurz warten
                    await asyncio.sleep(2)
                    
            except Exception as e:
                logger.error(f"Fehler im Queue-Worker: {e}")
                await asyncio.sleep(5)
                
    async def _start_task(self, task: ProcessingTask):
        """Startet eine einzelne Verarbeitungsaufgabe"""
        try:
            # Eindeutige Instanz-ID generieren
            task.instance_id = f"inst_{task.task_id.split('_')[-1]}"
            
            # Task zu laufenden Tasks hinzufügen
            async with self.running_lock:
                task.status = QueueStatus.RUNNING
                task.started_at = datetime.now()
                self.running_tasks[task.task_id] = task
                
            logger.info(f"Starte Verarbeitung für Task {task.task_id} (Instanz {task.instance_id})")
            
            # Background-Task für WebODM-CLI starten
            asyncio.create_task(self._process_task(task))
            
        except Exception as e:
            logger.error(f"Fehler beim Starten der Task {task.task_id}: {e}")
            await self._complete_task(task.task_id, QueueStatus.FAILED, str(e))
            
    async def _process_task(self, task: ProcessingTask):
        """Führt die WebODM-CLI Verarbeitung mit paralleler Instanz aus"""
        try:
            from services.webodm_cli_service import get_webodm_cli_service
            
            webodm_service = await get_webodm_cli_service()
            
            logger.info(f"Starte WebODM-CLI Instanz {task.instance_id} für Task {task.task_id}")
            
            # WebODM-CLI Verarbeitung mit Instanz-ID starten
            result = await webodm_service.process_images(
                project_path=task.project_path,
                images_path=task.images_path,
                options=task.options,
                instance_id=task.instance_id
            )
            
            # Ergebnis verarbeiten
            if result["status"] == "completed":
                await self._complete_task(task.task_id, QueueStatus.COMPLETED)
                
                # Aufräumen (behält Ergebnisse, löscht Temp-Dateien)
                await webodm_service.cleanup_project(task.project_path, keep_results=True)
                
                logger.info(f"WebODM-CLI Instanz {task.instance_id} erfolgreich abgeschlossen")
            else:
                await self._complete_task(
                    task.task_id, 
                    QueueStatus.FAILED, 
                    result.get("message", "Unbekannter Fehler")
                )
                
                logger.error(f"WebODM-CLI Instanz {task.instance_id} fehlgeschlagen: {result.get('message')}")
                
        except Exception as e:
            logger.error(f"Fehler bei Task-Verarbeitung {task.task_id} (Instanz {task.instance_id}): {e}")
            await self._complete_task(task.task_id, QueueStatus.FAILED, str(e))
            
    async def _complete_task(self, task_id: str, status: QueueStatus, error_message: str = None):
        """Schließt eine Task ab"""
        async with self.running_lock:
            if task_id in self.running_tasks:
                task = self.running_tasks.pop(task_id)
                task.status = status
                task.completed_at = datetime.now()
                task.error_message = error_message
                
                # Zu abgeschlossenen Tasks hinzufügen
                self.completed_tasks[task_id] = task
                
                # Alte abgeschlossene Tasks aufräumen (max 1000)
                if len(self.completed_tasks) > 1000:
                    oldest_tasks = sorted(
                        self.completed_tasks.items(),
                        key=lambda x: x[1].completed_at
                    )[:100]
                    
                    for old_task_id, _ in oldest_tasks:
                        del self.completed_tasks[old_task_id]
                        
                await self.save_queue_state()
                
                logger.info(f"Task {task_id} abgeschlossen: {status.value} (Instanz {task.instance_id})")
                
    def _estimate_wait_time(self, queue_position: int) -> int:
        """Schätzt die Wartezeit in Minuten (mit parallelen WebODM-CLI Instanzen)"""
        # Durchschnittliche Verarbeitungszeit: 12 Minuten pro Task (parallele Verarbeitung ist effizienter)
        avg_processing_time = 12
        
        # Berücksichtigung der laufenden Tasks
        running_count = len(self.running_tasks)
        remaining_slots = max(0, self.max_concurrent_jobs - running_count)
        
        if queue_position <= remaining_slots:
            return 0  # Kann sofort starten
        else:
            # Wartezeit basierend auf Position und verfügbaren parallelen Slots
            tasks_ahead = queue_position - remaining_slots
            parallel_batches = (tasks_ahead + self.max_concurrent_jobs - 1) // self.max_concurrent_jobs
            return parallel_batches * avg_processing_time
            
    def _task_to_dict(self, task: ProcessingTask) -> Dict:
        """Konvertiert Task zu Dictionary"""
        return {
            "task_id": task.task_id,
            "project_id": task.project_id,
            "status": task.status.value,
            "progress": task.progress,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "error_message": task.error_message,
            "instance_id": task.instance_id
        }
        
    async def save_queue_state(self):
        """Speichert Queue-Status in Datei"""
        try:
            state = {
                "queue": [self._task_to_dict(task) for task in self.queue],
                "running": [self._task_to_dict(task) for task in self.running_tasks.values()],
                "completed": [self._task_to_dict(task) for task in list(self.completed_tasks.values())[-100:]]  # Nur letzte 100
            }
            
            with open(self.queue_file, 'w') as f:
                json.dump(state, f, indent=2)
                
        except Exception as e:
            logger.error(f"Fehler beim Speichern des Queue-Status: {e}")
            
    async def load_queue_state(self):
        """Lädt Queue-Status aus Datei"""
        try:
            if not self.queue_file.exists():
                return
                
            with open(self.queue_file, 'r') as f:
                state = json.load(f)
                
            # Queue wiederherstellen
            for task_data in state.get("queue", []):
                task = self._dict_to_task(task_data)
                self.queue.append(task)
                
            # Laufende Tasks als fehlgeschlagen markieren (Server-Neustart)
            for task_data in state.get("running", []):
                task = self._dict_to_task(task_data)
                task.status = QueueStatus.FAILED
                task.error_message = "Server-Neustart während Verarbeitung"
                task.completed_at = datetime.now()
                self.completed_tasks[task.task_id] = task
                
            # Abgeschlossene Tasks wiederherstellen
            for task_data in state.get("completed", []):
                task = self._dict_to_task(task_data)
                self.completed_tasks[task.task_id] = task
                
            logger.info(f"Queue-Status geladen: {len(self.queue)} wartende Tasks")
            
        except Exception as e:
            logger.error(f"Fehler beim Laden des Queue-Status: {e}")
            
    def _dict_to_task(self, data: Dict) -> ProcessingTask:
        """Konvertiert Dictionary zu Task"""
        return ProcessingTask(
            task_id=data["task_id"],
            project_id=data["project_id"],
            reseller_id=data.get("reseller_id", ""),
            user_id=data.get("user_id", 0),
            project_path=data.get("project_path", ""),
            images_path=data.get("images_path", ""),
            options=data.get("options", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            status=QueueStatus(data["status"]),
            progress=data.get("progress", 0),
            error_message=data.get("error_message"),
            instance_id=data.get("instance_id")
        )


# Globale Queue-Manager-Instanz mit automatischer CPU-Erkennung
processing_queue = ProcessingQueueManager()


async def get_processing_queue() -> ProcessingQueueManager:
    """Dependency für FastAPI"""
    return processing_queue