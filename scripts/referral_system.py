#!/usr/bin/env python3
"""
referral_system.py — Automated referral tracking
"""

import json
import uuid
from datetime import datetime

class ReferralSystem:
    def __init__(self, data_file="data/referrals.json"):
        self.data_file = data_file
        self.referrals = self.load_data()
    
    def load_data(self):
        try:
            with open(self.data_file) as f:
                return json.load(f)
        except FileNotFoundError:
            return {"referrers": {}, "referrals": []}
    
    def save_data(self):
        import os
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w') as f:
            json.dump(self.referrals, f, indent=2)
    
    def generate_code(self, user_id):
        """Generate unique referral code for user"""
        code = str(uuid.uuid4())[:8].upper()
        self.referrals["referrers"][code] = {
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "referrals_count": 0,
            "rewards_earned": 0
        }
        self.save_data()
        return code
    
    def track_referral(self, referral_code, new_user_id):
        """Track successful referral"""
        if referral_code not in self.referrals["referrers"]:
            return False
        
        referrer = self.referrals["referrers"][referral_code]
        
        # Record referral
        self.referrals["referrals"].append({
            "referral_code": referral_code,
            "referrer_id": referrer["user_id"],
            "new_user_id": new_user_id,
            "timestamp": datetime.now().isoformat(),
            "rewarded": False
        })
        
        # Update referrer stats
        referrer["referrals_count"] += 1
        referrer["rewards_earned"] += 1  # 1 free month
        
        self.save_data()
        return True
    
    def get_referral_stats(self, user_id):
        """Get stats for user"""
        for code, data in self.referrals["referrers"].items():
            if data["user_id"] == user_id:
                return {
                    "code": code,
                    "referrals": data["referrals_count"],
                    "rewards": data["rewards_earned"]
                }
        return None

if __name__ == "__main__":
    ref = ReferralSystem()
    # Test
    code = ref.generate_code("test_user_123")
    print(f"Referral code: {code}")
