from typing import Dict, Any, List

class ComplianceService:
    @staticmethod
    def evaluate_summary_stats(active_members: List[Dict[str, Any]], is_bay: bool) -> Dict[str, Any]:
        """
        Calculates compliance scorecard from the audited structural members list.
        """
        compliant_count = sum(1 for m in active_members if m.get('status') == 'COMPLIANT')
        total_audited = len(active_members)

        return {
            'compliant_items': compliant_count,
            'total_items': total_audited,
            'compliance_pct': round((compliant_count / total_audited) * 100.0, 1) if total_audited > 0 else 100.0,
            'active_status': 'BAY CROSSING' if is_bay else 'INLAND BASELINE',
            'overall_status': 'COMPLIANT' if compliant_count >= total_audited - 2 else 'ACTION REQUIRED'
        }
