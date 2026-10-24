"""Identity resolution engine for Ghost Data Still Exists.

Resolves current and historical user identities, hashes, phone numbers, and references.
"""

import csv
import hashlib
from typing import Dict, Set, Optional, Any

class IdentityResolver:
    def __init__(self, identities_csv_path: str, audit_log_csv_path: str):
        self.identities_csv_path = identities_csv_path
        self.audit_log_csv_path = audit_log_csv_path
        
        self.users: Dict[str, Dict[str, Any]] = {}
        self.user_idents: Dict[str, Dict[str, Any]] = {}
        self.uid_by_email: Dict[str, str] = {}
        self.uid_by_phone: Dict[str, str] = {}
        self.uid_by_hash: Dict[str, str] = {}
        self.uid_by_name: Dict[str, str] = {}
        
        self._load()

    @staticmethod
    def normalize_email(email: str) -> str:
        if not email:
            return ""
        return email.strip().lower()

    @staticmethod
    def compute_sha256(val: str) -> str:
        if not val:
            return ""
        return hashlib.sha256(val.strip().lower().encode('utf-8')).hexdigest()

    def _load(self):
        # 1. Load current identities
        with open(self.identities_csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
                uid = r['user_id'].strip()
                self.users[uid] = r
                
                norm_email = self.normalize_email(r.get('email', ''))
                phone = r.get('phone', '').strip()
                name = r.get('name', '').strip()
                em_hash = r.get('email_hash', '').strip().lower()
                
                self.user_idents[uid] = {
                    'uid': uid,
                    'emails': {norm_email} if norm_email else set(),
                    'phones': {phone} if phone else set(),
                    'names': {name} if name else set(),
                    'hashes': {em_hash} if em_hash else set(),
                }
                
                if norm_email:
                    self.uid_by_email[norm_email] = uid
                if phone:
                    self.uid_by_phone[phone] = uid
                if em_hash:
                    self.uid_by_hash[em_hash] = uid
                if name:
                    self.uid_by_name[name] = uid

        # 2. Ingest historical identity changes from audit log
        with open(self.audit_log_csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for r in reader:
                uid = r['user_id'].strip()
                if uid not in self.user_idents:
                    continue
                
                fn = r.get('field_name', '').strip()
                old_v = r.get('old_value', '').strip()
                new_v = r.get('new_value', '').strip()
                
                if fn == 'email':
                    for v in (old_v, new_v):
                        norm = self.normalize_email(v)
                        if norm:
                            self.user_idents[uid]['emails'].add(norm)
                            self.uid_by_email[norm] = uid
                            h = self.compute_sha256(norm)
                            self.user_idents[uid]['hashes'].add(h)
                            self.uid_by_hash[h] = uid
                elif fn == 'phone':
                    for v in (old_v, new_v):
                        if v:
                            self.user_idents[uid]['phones'].add(v)
                            self.uid_by_phone[v] = uid
                elif fn == 'name':
                    for v in (old_v, new_v):
                        if v:
                            self.user_idents[uid]['names'].add(v)
                            self.uid_by_name[v] = uid

    def add_alias(self, user_id: str, email: Optional[str] = None, phone: Optional[str] = None):
        if user_id in self.user_idents:
            if email:
                ne = self.normalize_email(email)
                self.user_idents[user_id]['emails'].add(ne)
                self.uid_by_email[ne] = user_id
                h = self.compute_sha256(ne)
                self.user_idents[user_id]['hashes'].add(h)
                self.uid_by_hash[h] = user_id
            if phone:
                p = phone.strip()
                self.user_idents[user_id]['phones'].add(p)
                self.uid_by_phone[p] = user_id

    def resolve_uid(
        self,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        user_id: Optional[str] = None,
        email_hash: Optional[str] = None,
        name: Optional[str] = None
    ) -> Optional[str]:
        if user_id:
            uid_clean = user_id.strip()
            if uid_clean in self.user_idents:
                return uid_clean
        if email:
            norm = self.normalize_email(email)
            if norm in self.uid_by_email:
                return self.uid_by_email[norm]
        if phone:
            p = phone.strip()
            if p in self.uid_by_phone:
                return self.uid_by_phone[p]
        if email_hash:
            h = email_hash.strip().lower()
            if h in self.uid_by_hash:
                return self.uid_by_hash[h]
        if name:
            n = name.strip()
            if n in self.uid_by_name:
                return self.uid_by_name[n]
        return None

    def get_identities(self, user_id: str) -> Optional[Dict[str, Any]]:
        return self.user_idents.get(user_id)
