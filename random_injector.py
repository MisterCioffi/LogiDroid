#!/usr/bin/env python3
"""
LogiDroid Random Action Injector
Sistema di iniezione azioni casuali per rompere pattern monotoni dell'LLM
"""

import random
import subprocess
import time
import os
from datetime import datetime

class RandomActionInjector:
    def __init__(self, frequency=6):
        """
        Inizializza il sistema di random injection
        
        Args:
            frequency (int): Ogni quante iterazioni iniettare azione random
        """
        # Carica configurazione da config.json
        self.config = self._load_config()
        
        # Usa configurazione da file se disponibile, altrimenti usa parametro
        random_config = self.config.get("random_injection", {})
        self.enabled = random_config.get("enabled", True)
        self.frequency = random_config.get("frequency", frequency)
        
        # Carica contatore persistente
        self.action_count = self._load_action_count()
        
        # Lista azioni configurabile - Solo swipe verticali
        default_actions = ["SWIPE_UP", "SWIPE_DOWN"]
        self.random_actions = random_config.get("actions", default_actions)
        
        print(f"🎲 Random Injector initialized:")
        print(f"   Enabled: {self.enabled}")
        print(f"   Frequency: Every {self.frequency} actions")
        print(f"   Current count: {self.action_count}")
        print(f"   Available actions: {len(self.random_actions)}")
    
    def _load_action_count(self):
        """Carica il contatore persistente dalle iterazioni precedenti"""
        try:
            count_file = "test/prompts/random_action_count.txt"
            if os.path.exists(count_file):
                with open(count_file, 'r') as f:
                    count = int(f.read().strip())
                    return count
        except:
            pass
        return 0
    
    def _save_action_count(self):
        """Salva il contatore per la prossima iterazione"""
        try:
            count_file = "test/prompts/random_action_count.txt"
            os.makedirs(os.path.dirname(count_file), exist_ok=True)
            with open(count_file, 'w') as f:
                f.write(str(self.action_count))
        except Exception as e:
            print(f"⚠️ Could not save action count: {e}")
    
    def _load_config(self):
        """Carica configurazione da config.json"""
        try:
            import json
            with open('config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}  # Usa defaults se non riesce a caricare
        
    def should_inject_random(self):
        """
        Determina se inserire azione random basata sulla frequenza e configurazione
        
        Returns:
            bool: True se è il momento di iniettare azione random
        """
        if not self.enabled:
            return False
            
        self.action_count += 1
        self._save_action_count()  # Salva il contatore aggiornato
        
        should_inject = self.action_count % self.frequency == 0
        
        if should_inject:
            print(f"🎲 Random injection triggered! (Count: {self.action_count})")
        else:
            print(f"📊 Action count: {self.action_count}/{self.frequency} (next random at {self.frequency - (self.action_count % self.frequency)} actions)")
            
        return should_inject
    
    def get_random_action(self):
        """
        Seleziona azione random dalla lista disponibile
        
        Returns:
            str: Azione random da eseguire
        """
        action = random.choice(self.random_actions)
        print(f"🎯 Selected random action: {action}")
        return action
    
    def execute_random_action(self, action):
        """
        Esegue l'azione random selezionata via ADB
        
        Args:
            action (str): Azione da eseguire
            
        Returns:
            bool: True se eseguita con successo
        """
        print(f"🎲 EXECUTING RANDOM ACTION: {action}")
        
        try:
            if action == "SWIPE_UP":
                # Swipe dal centro-basso verso centro-alto
                subprocess.run(["adb", "shell", "input", "swipe", "540", "1500", "540", "500"], check=True)
                print("⬆️ Executed: SWIPE UP")
                
            elif action == "SWIPE_DOWN":
                # Swipe dal centro-alto verso centro-basso
                subprocess.run(["adb", "shell", "input", "swipe", "540", "500", "540", "1500"], check=True)
                print("⬇️ Executed: SWIPE DOWN")
                
            else:
                print(f"❌ Unknown random action: {action}")
                return False
                
            # Attesa per stabilizzazione UI dopo azione random
            print("⏳ Waiting for UI stabilization after random action...")
            time.sleep(3)  # 3 secondi per stabilizzazione
            
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error executing random action {action}: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error in random action {action}: {e}")
            return False
    
    def full_random_cycle(self):
        """
        Esegue un ciclo completo di random injection:
        1. Seleziona azione random
        2. Esegue l'azione
        3. Cattura nuova schermata
        4. Converte in JSON
        
        Returns:
            str: Path al nuovo file JSON generato, None se errore
        """
        print("🎲 " + "="*50)
        print("🎲 STARTING RANDOM INJECTION CYCLE")
        print("🎲 " + "="*50)
        
        # 1. Seleziona e esegui azione random
        random_action = self.get_random_action()
        
        if not self.execute_random_action(random_action):
            print("❌ Random action failed, aborting cycle")
            return None
        
        # 2. Cattura nuova schermata dopo azione random
        timestamp = int(time.time())
        xml_file = f"test/xml/random_{timestamp}.xml"
        json_file = f"test/json/result_random_{timestamp}.json"
        
        print("📸 Capturing new screen after random action...")
        
        try:
            # Cattura XML
            subprocess.run(["adb", "shell", "uiautomator", "dump", "/sdcard/ui_dump_random.xml"], check=True)
            subprocess.run(["adb", "pull", "/sdcard/ui_dump_random.xml", xml_file], check=True)
            
            # Conversione XML → JSON
            subprocess.run(["python3", "xml_to_json.py", xml_file, json_file], check=True)
            
            print(f"✅ Random cycle completed! New screen: {json_file}")
            
            # Reset action count per evitare random consecutivi
            self.action_count = 0
            
            # Salva azione random nella history per l'LLM
            self._save_random_action_to_history(random_action)
            
            return json_file
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error capturing screen after random action: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error in random cycle: {e}")
            return None
    
    def _save_random_action_to_history(self, action):
        """
        Salva l'azione random nella cronologia per l'LLM
        
        Args:
            action (str): Azione random eseguita
        """
        try:
            import json
            
            history_file = "test/prompts/action_history.json"
            os.makedirs(os.path.dirname(history_file), exist_ok=True)
            
            # Carica cronologia esistente
            history = []
            if os.path.exists(history_file):
                with open(history_file, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            
            # Aggiungi azione random
            history.append({
                "timestamp": datetime.now().isoformat(),
                "action": f"RANDOM:{action}",
                "success": True,
                "screen": f"Random action executed: {action}"
            })
            
            # Mantieni solo le ultime 10 azioni
            if len(history) > 10:
                history = history[-10:]
            
            # Salva cronologia aggiornata
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
                
            print(f"💾 Random action saved to history: RANDOM:{action}")
            
        except Exception as e:
            print(f"⚠️ Could not save random action to history: {e}")
    
    def reset_counter(self):
        """Reset del contatore per debugging o nuovo test"""
        self.action_count = 0
        self._save_action_count()
        print("🔄 Random injection counter reset")

# Test del modulo
if __name__ == "__main__":
    print("🧪 Testing Random Action Injector...")
    
    injector = RandomActionInjector(frequency=3)  # Test con frequenza bassa
    
    # Simula alcune iterazioni
    for i in range(5):
        print(f"\n--- Iteration {i+1} ---")
        if injector.should_inject_random():
            result = injector.full_random_cycle()
            if result:
                print(f"✅ Random cycle successful: {result}")
            else:
                print("❌ Random cycle failed")
        else:
            print("📱 Normal LLM iteration (no random)")
