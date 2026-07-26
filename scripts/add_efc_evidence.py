#!/usr/bin/env python3
"""
Add DOI evidence to EFC relationships in Neo4j graph.

This script updates high-confidence relationships that reference EFC theory
to include proper DOI citations from published papers.
"""

from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

# EFC DOI mappings from published papers
EFC_DOIS = {
    "efc_master": "doi:10.6084/m9.figshare.30630500",  # Main EFC theory
    "symbiosis": "doi:10.6084/m9.figshare.30773684",   # Symbiosis paper
    "cem": "doi:10.6084/m9.figshare.30275947",         # CEM framework
    "mcp_tools": "doi:10.6084/m9.figshare.28337030"    # MCP tools
}

def add_evidence_to_efc_relationships(dry_run=True):
    """Add DOI evidence to EFC-related relationships."""
    
    driver = GraphDatabase.driver(
        os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        auth=(os.getenv('NEO4J_USER', 'neo4j'), os.getenv('NEO4J_PASSWORD', 'password'))
    )
    
    with driver.session() as session:
        # Update relationships mentioning EFC core concepts
        queries = [
            # Energy-Flow Cosmology references
            {
                "name": "EFC Theory References",
                "pattern": "(?i).*(energy.flow|efc|cosmology).*",
                "doi": EFC_DOIS["efc_master"],
                "epistemic": "established"
            },
            # Symbiosis framework
            {
                "name": "Symbiosis References",
                "pattern": "(?i).*(symbiosis|human.ai|co.reflection).*",
                "doi": EFC_DOIS["symbiosis"],
                "epistemic": "established"
            },
            # CEM framework
            {
                "name": "CEM References",
                "pattern": "(?i).*(consciousness|ego|mirror|cem).*",
                "doi": EFC_DOIS["cem"],
                "epistemic": "established"
            }
        ]
        
        total_updated = 0
        
        for q in queries:
            # Count how many would be updated
            count_result = session.run(f'''
                MATCH (n)-[r]->(m)
                WHERE (n.name =~ $pattern OR m.name =~ $pattern)
                AND r.confidence > 0.7
                AND r.evidence IS NULL
                RETURN count(r) as count
            ''', pattern=q["pattern"])
            
            count = count_result.single()['count']
            
            if dry_run:
                print(f'\n🔍 {q["name"]}: {count:,} relationships would be updated')
                print(f'   DOI: {q["doi"]}')
                print(f'   Epistemic status: {q["epistemic"]}')
            else:
                # Actually update
                result = session.run(f'''
                    MATCH (n)-[r]->(m)
                    WHERE (n.name =~ $pattern OR m.name =~ $pattern)
                    AND r.confidence > 0.7
                    AND r.evidence IS NULL
                    SET r.evidence = $doi,
                        r.epistemic_status = $epistemic
                    RETURN count(r) as updated
                ''', pattern=q["pattern"], doi=q["doi"], epistemic=q["epistemic"])
                
                updated = result.single()['updated']
                total_updated += updated
                print(f'\n✅ {q["name"]}: {updated:,} relationships updated')
                print(f'   DOI: {q["doi"]}')
        
        if not dry_run:
            print(f'\n📊 Total updated: {total_updated:,} relationships')
            
            # Show final stats
            result = session.run('''
                MATCH ()-[r]->()
                WHERE r.confidence > 0.7
                RETURN 
                    count(r) as total,
                    sum(CASE WHEN r.evidence IS NOT NULL THEN 1 ELSE 0 END) as with_evidence
            ''')
            
            stats = result.single()
            total = stats['total']
            with_ev = stats['with_evidence']
            coverage = (with_ev / total * 100) if total > 0 else 0
            
            print(f'\n📈 Final Evidence Coverage:')
            print(f'   High-confidence relationships: {total:,}')
            print(f'   With evidence: {with_ev:,}')
            print(f'   Coverage: {coverage:.1f}%')
    
    driver.close()

if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("EFC Evidence Backfill Script")
    print("=" * 60)
    
    if "--execute" in sys.argv:
        print("\n⚠️  EXECUTING UPDATES (not a dry run)\n")
        add_evidence_to_efc_relationships(dry_run=False)
    else:
        print("\n🔍 DRY RUN MODE (use --execute to actually update)")
        print("=" * 60)
        add_evidence_to_efc_relationships(dry_run=True)
        print("\n💡 Run with --execute to apply these changes")
