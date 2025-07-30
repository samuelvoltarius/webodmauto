#!/usr/bin/env python3
"""
ChiliView Production Cleanup Script
Automatische Bereinigung von Debug-Code und unprofessionellen UI-Elementen
"""

import os
import re
import glob
from pathlib import Path

class ProductionCleanup:
    def __init__(self, base_path="local_dev/frontend/src"):
        self.base_path = Path(base_path)
        self.changes_made = []
        
    def log_change(self, file_path, change_type, old_content, new_content):
        """Protokolliert vorgenommene Änderungen"""
        self.changes_made.append({
            'file': str(file_path),
            'type': change_type,
            'old': old_content.strip(),
            'new': new_content.strip()
        })
    
    def cleanup_console_logs(self, content, file_path):
        """Entfernt oder schützt console.log Aufrufe"""
        changes = 0
        
        # console.log mit DEV-Guard versehen
        pattern = r'(\s*)console\.log\((.*?)\)'
        def replace_console_log(match):
            nonlocal changes
            indent = match.group(1)
            args = match.group(2)
            
            # Bereits geschützte Logs überspringen
            if 'import.meta.env.DEV' in args:
                return match.group(0)
            
            changes += 1
            old_content = match.group(0)
            new_content = f"{indent}if (import.meta.env.DEV) {{\n{indent}  console.log({args})\n{indent}}}"
            
            self.log_change(file_path, 'console.log -> DEV guard', old_content, new_content)
            return new_content
        
        content = re.sub(pattern, replace_console_log, content, flags=re.MULTILINE)
        
        # console.error durch proper error handling ersetzen
        pattern = r'(\s*)console\.error\([\'"]([^\'"]*)[\'"],?\s*([^)]*)\)'
        def replace_console_error(match):
            nonlocal changes
            indent = match.group(1)
            message = match.group(2)
            
            changes += 1
            old_content = match.group(0)
            new_content = f"{indent}// Error logged: {message}"
            
            self.log_change(file_path, 'console.error removed', old_content, new_content)
            return new_content
        
        content = re.sub(pattern, replace_console_error, content, flags=re.MULTILINE)
        
        return content, changes
    
    def cleanup_alerts(self, content, file_path):
        """Ersetzt alert() durch showMessage()"""
        changes = 0
        
        # alert() durch showMessage() ersetzen
        pattern = r'alert\([\'"]([^\'"]*)[\'"]?\)'
        def replace_alert(match):
            nonlocal changes
            message = match.group(1)
            
            changes += 1
            old_content = match.group(0)
            new_content = f"showMessage('{message}', 'info')"
            
            self.log_change(file_path, 'alert -> showMessage', old_content, new_content)
            return new_content
        
        content = re.sub(pattern, replace_alert, content)
        
        # Erfolgs-Alerts als success
        pattern = r'alert\([\'"]([^\'"]*(erfolgreich|erstellt|gespeichert|gelöscht|aktualisiert)[^\'"]*)[\'"]?\)'
        def replace_success_alert(match):
            nonlocal changes
            message = match.group(1)
            
            changes += 1
            old_content = match.group(0)
            new_content = f"showMessage('{message}', 'success')"
            
            self.log_change(file_path, 'success alert -> showMessage', old_content, new_content)
            return new_content
        
        content = re.sub(pattern, replace_success_alert, content, flags=re.IGNORECASE)
        
        # Fehler-Alerts als error
        pattern = r'alert\([\'"]([^\'"]*(fehler|error)[^\'"]*)[\'"]?\)'
        def replace_error_alert(match):
            nonlocal changes
            message = match.group(1)
            
            changes += 1
            old_content = match.group(0)
            new_content = f"showMessage('{message}', 'error')"
            
            self.log_change(file_path, 'error alert -> showMessage', old_content, new_content)
            return new_content
        
        content = re.sub(pattern, replace_error_alert, content, flags=re.IGNORECASE)
        
        return content, changes
    
    def cleanup_confirms(self, content, file_path):
        """Ersetzt confirm() durch showConfirmation()"""
        changes = 0
        
        # confirm() in if-statements
        pattern = r'if\s*\(\s*confirm\([\'"]([^\'"]*)[\'"]?\)\s*\)\s*\{([^}]*)\}'
        def replace_confirm(match):
            nonlocal changes
            message = match.group(1)
            action_code = match.group(2).strip()
            
            changes += 1
            old_content = match.group(0)
            new_content = f"showConfirmation('Bestätigung', '{message}', () => {{\n{action_code}\n}})"
            
            self.log_change(file_path, 'confirm -> showConfirmation', old_content, new_content)
            return new_content
        
        content = re.sub(pattern, replace_confirm, content, flags=re.DOTALL)
        
        return content, changes
    
    def add_required_imports(self, content, file_path):
        """Fügt benötigte Imports hinzu"""
        changes = 0
        
        # Prüfen ob showMessage verwendet wird
        if 'showMessage(' in content and 'inject(' not in content:
            # inject import hinzufügen
            if "import { " in content and "} from 'vue'" in content:
                pattern = r"import \{ ([^}]*) \} from 'vue'"
                def add_inject(match):
                    nonlocal changes
                    imports = match.group(1)
                    if 'inject' not in imports:
                        changes += 1
                        new_imports = imports + ', inject'
                        old_content = match.group(0)
                        new_content = f"import {{ {new_imports} }} from 'vue'"
                        self.log_change(file_path, 'add inject import', old_content, new_content)
                        return new_content
                    return match.group(0)
                
                content = re.sub(pattern, add_inject, content)
            
            # showMessage injection hinzufügen
            if 'const showMessage = inject(' not in content:
                # Nach setup() function suchen
                pattern = r'(setup\(\)\s*\{)'
                def add_injection(match):
                    nonlocal changes
                    changes += 1
                    old_content = match.group(0)
                    new_content = match.group(0) + "\n    const showMessage = inject('showMessage')\n"
                    self.log_change(file_path, 'add showMessage injection', old_content, new_content)
                    return new_content
                
                content = re.sub(pattern, add_injection, content)
        
        return content, changes
    
    def cleanup_debug_comments(self, content, file_path):
        """Entfernt Debug-Kommentare"""
        changes = 0
        
        # TODO/FIXME/HACK Kommentare entfernen
        patterns = [
            r'//\s*(TODO|FIXME|HACK|XXX|BUG|NOTE|TEMP|DEBUG):?.*\n',
            r'/\*\s*(TODO|FIXME|HACK|XXX|BUG|NOTE|TEMP|DEBUG):?.*?\*/\n?'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, flags=re.IGNORECASE | re.DOTALL)
            if matches:
                changes += len(matches)
                for match in matches:
                    self.log_change(file_path, 'debug comment removed', match, '')
                content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
        
        return content, changes
    
    def process_file(self, file_path):
        """Verarbeitet eine einzelne Datei"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            content = original_content
            total_changes = 0
            
            # Verschiedene Cleanup-Operationen
            content, changes = self.cleanup_console_logs(content, file_path)
            total_changes += changes
            
            content, changes = self.cleanup_alerts(content, file_path)
            total_changes += changes
            
            content, changes = self.cleanup_confirms(content, file_path)
            total_changes += changes
            
            content, changes = self.add_required_imports(content, file_path)
            total_changes += changes
            
            content, changes = self.cleanup_debug_comments(content, file_path)
            total_changes += changes
            
            # Datei nur schreiben wenn Änderungen vorgenommen wurden
            if total_changes > 0:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✅ {file_path}: {total_changes} Änderungen")
            else:
                print(f"⏭️  {file_path}: Keine Änderungen erforderlich")
                
            return total_changes
            
        except Exception as e:
            print(f"❌ Fehler bei {file_path}: {e}")
            return 0
    
    def run_cleanup(self):
        """Führt das komplette Cleanup durch"""
        print("🧹 ChiliView Production Cleanup gestartet...")
        print("=" * 50)
        
        # Vue-Dateien finden
        vue_files = list(self.base_path.rglob("*.vue"))
        js_files = list(self.base_path.rglob("*.js"))
        
        all_files = vue_files + js_files
        total_changes = 0
        
        for file_path in all_files:
            changes = self.process_file(file_path)
            total_changes += changes
        
        print("=" * 50)
        print(f"✅ Cleanup abgeschlossen!")
        print(f"📁 {len(all_files)} Dateien verarbeitet")
        print(f"🔧 {total_changes} Änderungen insgesamt")
        
        # Änderungsprotokoll erstellen
        self.create_change_log()
    
    def create_change_log(self):
        """Erstellt ein Protokoll aller Änderungen"""
        if not self.changes_made:
            return
        
        log_path = self.base_path.parent / "CLEANUP_LOG.md"
        
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write("# Production Cleanup Log\n\n")
            f.write(f"**Datum**: {os.popen('date').read().strip()}\n")
            f.write(f"**Änderungen**: {len(self.changes_made)}\n\n")
            
            # Gruppierung nach Dateien
            files = {}
            for change in self.changes_made:
                file_path = change['file']
                if file_path not in files:
                    files[file_path] = []
                files[file_path].append(change)
            
            for file_path, changes in files.items():
                f.write(f"## {file_path}\n\n")
                for change in changes:
                    f.write(f"### {change['type']}\n")
                    f.write("**Vorher:**\n```javascript\n")
                    f.write(change['old'])
                    f.write("\n```\n\n**Nachher:**\n```javascript\n")
                    f.write(change['new'])
                    f.write("\n```\n\n")
        
        print(f"📋 Änderungsprotokoll erstellt: {log_path}")

def main():
    """Hauptfunktion"""
    cleanup = ProductionCleanup()
    cleanup.run_cleanup()

if __name__ == "__main__":
    main()