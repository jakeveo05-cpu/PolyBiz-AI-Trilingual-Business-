"""
Database Backup - Automated backup for SQLite database
"""
import os
import shutil
import gzip
from datetime import datetime, timedelta
from pathlib import Path
import logging

logger = logging.getLogger('polybiz.backup')


class DatabaseBackup:
    """
    Handle database backups
    - Daily automatic backups
    - Compressed storage
    - Retention policy (keep last N backups)
    """
    
    def __init__(
        self,
        db_path: str = "data/polybiz.db",
        backup_dir: str = "data/backups",
        max_backups: int = 7,
        compress: bool = True
    ):
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.max_backups = max_backups
        self.compress = compress
        
        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(self, suffix: str = "") -> str:
        """
        Create a backup of the database
        
        Args:
            suffix: Optional suffix for backup filename
            
        Returns:
            Path to backup file
        """
        if not self.db_path.exists():
            logger.warning(f"Database not found: {self.db_path}")
            return None
        
        # Generate backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"polybiz_{timestamp}{suffix}.db"
        
        if self.compress:
            backup_name += ".gz"
        
        backup_path = self.backup_dir / backup_name
        
        try:
            if self.compress:
                # Compressed backup
                with open(self.db_path, 'rb') as f_in:
                    with gzip.open(backup_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                # Simple copy
                shutil.copy2(self.db_path, backup_path)
            
            logger.info(f"Backup created: {backup_path}")
            
            # Cleanup old backups
            self._cleanup_old_backups()
            
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return None
    
    def restore_backup(self, backup_path: str) -> bool:
        """
        Restore database from backup
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if successful
        """
        backup_path = Path(backup_path)
        
        if not backup_path.exists():
            logger.error(f"Backup not found: {backup_path}")
            return False
        
        try:
            # Create backup of current database before restore
            if self.db_path.exists():
                self.create_backup(suffix="_pre_restore")
            
            if str(backup_path).endswith('.gz'):
                # Decompress and restore
                with gzip.open(backup_path, 'rb') as f_in:
                    with open(self.db_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                # Simple copy
                shutil.copy2(backup_path, self.db_path)
            
            logger.info(f"Database restored from: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            return False
    
    def _cleanup_old_backups(self):
        """Remove old backups beyond retention limit"""
        backups = sorted(
            self.backup_dir.glob("polybiz_*.db*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )
        
        # Keep only max_backups
        for old_backup in backups[self.max_backups:]:
            try:
                old_backup.unlink()
                logger.info(f"Removed old backup: {old_backup}")
            except Exception as e:
                logger.error(f"Failed to remove old backup: {e}")
    
    def list_backups(self) -> list:
        """List all available backups"""
        backups = []
        
        for backup_file in sorted(
            self.backup_dir.glob("polybiz_*.db*"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        ):
            stat = backup_file.stat()
            backups.append({
                "path": str(backup_file),
                "filename": backup_file.name,
                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                "created": datetime.fromtimestamp(stat.st_mtime).isoformat()
            })
        
        return backups
    
    def get_latest_backup(self) -> str:
        """Get path to most recent backup"""
        backups = self.list_backups()
        return backups[0]["path"] if backups else None


# Scheduled backup task
async def scheduled_backup():
    """Task for scheduled backups (call from scheduler)"""
    backup = DatabaseBackup()
    result = backup.create_backup()
    
    if result:
        logger.info(f"Scheduled backup completed: {result}")
    else:
        logger.error("Scheduled backup failed")
    
    return result


# Global backup instance
_backup: DatabaseBackup = None


def get_backup_manager() -> DatabaseBackup:
    """Get or create global backup manager"""
    global _backup
    if _backup is None:
        _backup = DatabaseBackup()
    return _backup
