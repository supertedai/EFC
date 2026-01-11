-- ============================================
-- Neo4j Canonical Life Schema
-- ============================================
-- Complete constraints and indexes for
-- personal canonical fact storage
-- ============================================

-- === Core Nodes ===

CREATE CONSTRAINT user_id_unique IF NOT EXISTS
FOR (u:User)
REQUIRE u.id IS UNIQUE;

CREATE CONSTRAINT person_name_unique IF NOT EXISTS
FOR (p:Person)
REQUIRE p.name IS UNIQUE;

CREATE CONSTRAINT asset_name_type_unique IF NOT EXISTS
FOR (a:Asset)
REQUIRE (a.name, a.type) IS UNIQUE;

CREATE CONSTRAINT location_name_unique IF NOT EXISTS
FOR (l:Location)
REQUIRE l.name IS UNIQUE;

CREATE CONSTRAINT project_name_unique IF NOT EXISTS
FOR (p:Project)
REQUIRE p.name IS UNIQUE;

CREATE CONSTRAINT theory_name_unique IF NOT EXISTS
FOR (t:Theory)
REQUIRE t.name IS UNIQUE;

CREATE CONSTRAINT organization_name_unique IF NOT EXISTS
FOR (o:Organization)
REQUIRE o.name IS UNIQUE;

CREATE CONSTRAINT skill_name_unique IF NOT EXISTS
FOR (s:Skill)
REQUIRE s.name IS UNIQUE;

-- === Indexes for Fast Temporal Queries ===

-- Status filtering (active vs archived)
CREATE INDEX rel_owns_status_index IF NOT EXISTS
FOR ()-[r:OWNS]-()
ON (r.status);

CREATE INDEX rel_located_status_index IF NOT EXISTS
FOR ()-[r:LOCATED_IN]-()
ON (r.status);

CREATE INDEX rel_works_status_index IF NOT EXISTS
FOR ()-[r:WORKS_AS]-()
ON (r.status);

-- Temporal range queries
CREATE INDEX rel_owns_since_index IF NOT EXISTS
FOR ()-[r:OWNS]-()
ON (r.since);

CREATE INDEX rel_owns_until_index IF NOT EXISTS
FOR ()-[r:OWNS]-()
ON (r.until);

CREATE INDEX rel_located_since_index IF NOT EXISTS
FOR ()-[r:LOCATED_IN]-()
ON (r.since);

CREATE INDEX rel_works_since_index IF NOT EXISTS
FOR ()-[r:WORKS_AS]-()
ON (r.since);

-- === Relationship Types (documented) ===

-- OWNERSHIP domain
-- (u:User)-[:OWNS {since, until, status}]->(a:Asset)

-- FAMILY domain
-- (u:User)-[:MARRIED_TO {since, until, status}]->(p:Person)
-- (u:User)-[:HAS_CHILD {since, status}]->(p:Person)
-- (u:User)-[:HAS_PARENT {since, status}]->(p:Person)
-- (u:User)-[:HAS_SIBLING {since, status}]->(p:Person)

-- LOCATION domain
-- (u:User)-[:LOCATED_IN {since, until, status, type}]->(l:Location)

-- WORK domain
-- (u:User)-[:WORKS_AS {role, since, until, status}]->(o:Organization)

-- PROJECTS domain
-- (u:User)-[:DEVELOPS {since, until, status}]->(p:Project)
-- (u:User)-[:MAINTAINS]->(p:Project)

-- SKILLS domain
-- (u:User)-[:HAS_SKILL {level, since}]->(s:Skill)

-- HEALTH domain
-- (u:User)-[:HAS_CONDITION {category, since, until}]->(c:Condition)
-- (u:User)-[:HAS_GENETIC_VARIANT {allele, since}]->(g:Gene)

-- THEORIES domain
-- (u:User)-[:AUTHORED]->(t:Theory)

-- === Common Relationship Properties ===
-- All temporal relationships should have:
-- - since: ISO 8601 datetime (when it started)
-- - until: ISO 8601 datetime or null (when it ended)
-- - status: 'active' or 'archived'
-- - confidence: 'canonical' (default for user assertions)
-- - source: 'user' (default)

-- === Queries for Testing ===

-- Get all active assets for user
-- MATCH (u:User {id:$user_id})-[r:OWNS {status:'active'}]->(a:Asset)
-- RETURN a.name, a.type, r.since
-- ORDER BY r.since DESC

-- Get historical ownership (including archived)
-- MATCH (u:User {id:$user_id})-[r:OWNS]->(a:Asset)
-- RETURN a.name, r.status, r.since, r.until
-- ORDER BY r.since DESC

-- Archive an asset (standard change pattern)
-- MATCH (u:User {id:$user_id})-[r:OWNS {status:'active'}]->(a:Asset)
-- WHERE toLower(a.name) CONTAINS toLower($asset_name)
-- SET r.status = 'archived', r.until = datetime()
-- RETURN a.name

-- Delete relationship (error correction only)
-- MATCH (u:User {id:$user_id})-[r:OWNS]->(a:Asset)
-- WHERE toLower(a.name) CONTAINS toLower($asset_name)
-- DELETE r
-- RETURN a.name
