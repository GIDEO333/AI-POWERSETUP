// Full 4-phase test with v2 guardrails
// Problem: "Should we migrate from PostgreSQL to MongoDB for a growing e-commerce platform?"
import { DialecticEngine } from './dist/engine.js';

const engine = new DialecticEngine();

function phase(label, input) {
  const r = engine.processPhase(input);
  console.log(`\n${'═'.repeat(60)}`);
  console.log(`${label}`);
  console.log(`${'═'.repeat(60)}`);
  
  if (r.summary.startsWith('ERROR:')) {
    console.log(`❌ ${r.summary}`);
    return r;
  }
  
  const emoji = { thesis: '📜', antithesis: '⚔️', synthesis: '🔀', stresstest: '🔥' };
  console.log(`${emoji[r.phase] || '•'} Phase: ${r.phase.toUpperCase()} — Complete`);
  console.log(`📋 Session: ${r.sessionId}`);
  console.log(`✅ Phases: [${r.phasesCompleted.join(' → ')}]`);
  
  if (r.assumptionCount > 0) console.log(`📌 Assumptions: ${r.assumptionCount}`);
  if (r.assumptionsSurvived !== null) console.log(`🛡️ Survived: ${r.assumptionsSurvived}/${r.assumptionCount}`);
  
  if (r.contradictionsFound.length > 0) {
    console.log(`⚠️ Contradictions: ${r.contradictionsFound.length}`);
    for (const c of r.contradictionsFound) {
      console.log(`   [${c.assumptionId}] keywords: ${c.keywords.join(', ')}`);
    }
  }
  
  if (r.sessionScore !== null) console.log(`📊 E(A) Score: ${r.sessionScore}`);
  if (r.confidence !== null) console.log(`🎯 Confidence: ${(r.confidence * 100).toFixed(0)}%`);
  console.log(`\n💬 ${r.summary}`);
  return r;
}

// ============================================================
// PHASE 1: THESIS — "Migrate to MongoDB"
// ============================================================
phase('PHASE 1: THESIS — Migrate PostgreSQL → MongoDB', {
  phase: 'thesis',
  content: `Our e-commerce platform should migrate from PostgreSQL to MongoDB. 
The product catalog has highly variable schemas (clothing has size/color, electronics has specs/compatibility, food has allergens/nutrition). 
PostgreSQL forces us to use JSONB columns or create dozens of product-type-specific tables, creating a maintenance nightmare. 
MongoDB's flexible document model would let each product type have its own natural schema without ALTER TABLE migrations. 
Additionally, our read-heavy workload (95% reads, 5% writes) is perfect for MongoDB's horizontal scaling via sharding.`,
  
  assumptions: [
    { id: 'A1', text: 'MongoDB flexible schema will eliminate the need for complex ALTER TABLE migrations when adding new product types' },
    { id: 'A2', text: 'MongoDB sharding will handle our read-heavy traffic better than PostgreSQL replication' },
    { id: 'A3', text: 'The team can migrate the existing relational data model to a document model without data integrity loss' },
    { id: 'A4', text: 'MongoDB operational costs will be lower than PostgreSQL at our scale' }
  ]
});

// ============================================================
// PHASE 2: ANTITHESIS — "Stay with PostgreSQL"
// ============================================================
phase('PHASE 2: ANTITHESIS — Stay with PostgreSQL', {
  phase: 'antithesis',
  content: `Migrating to MongoDB is a catastrophic mistake driven by schema-design laziness, not genuine technical need. 
PostgreSQL's JSONB with GIN indexes already handles flexible schemas beautifully — companies like Shopify run on PostgreSQL at massive scale. 
The real problem isn't the database, it's poor schema design. MongoDB sacrifices ACID transactions, which are CRITICAL for e-commerce (orders, payments, inventory decrements must be atomic). 
A failed payment that decrements inventory without completing the order is a business-ending bug.`,
  
  attacks: [
    { 
      assumptionId: 'A1', 
      counterExample: 'PostgreSQL JSONB with GIN indexes already provides flexible schema without migrations. Shopify processes millions of orders daily on PostgreSQL with highly variable product schemas. The real problem is poor table design, not database limitation.', 
      severity: 'high' 
    },
    { 
      assumptionId: 'A2', 
      counterExample: 'PostgreSQL read replicas with connection pooling (PgBouncer) handle read-heavy workloads efficiently. MongoDB sharding introduces massive operational complexity (config servers, mongos routers, shard keys) that a small team cannot maintain. Netflix moved AWAY from MongoDB to PostgreSQL for exactly this reason.', 
      severity: 'high' 
    },
    { 
      assumptionId: 'A3', 
      counterExample: 'E-commerce has deeply relational data: orders reference customers, customers reference addresses, orders contain line items referencing products, products reference categories and inventory. Flattening this into documents creates massive data duplication. When a product price changes, you must update every denormalized copy — a consistency nightmare.', 
      severity: 'fatal' 
    },
    { 
      assumptionId: 'A4', 
      counterExample: 'MongoDB licensing (Atlas) at enterprise scale costs 3-5x more than self-hosted PostgreSQL. MongoDB requires more storage due to document duplication and larger indexes. Operational costs increase because you need specialized MongoDB DBAs instead of leveraging the vast PostgreSQL talent pool.', 
      severity: 'high' 
    }
  ]
});

// ============================================================
// PHASE 3: SYNTHESIS — Merge
// ============================================================
phase('PHASE 3: SYNTHESIS — Merged Architecture', {
  phase: 'synthesis',
  content: `The synthesis is a hybrid "Polyglot Persistence" architecture:
1. KEEP PostgreSQL as the system of record for all transactional data (orders, payments, inventory, customers). ACID compliance is non-negotiable for financial operations.
2. USE PostgreSQL JSONB columns for the product catalog's flexible attributes (size, color, specs). Add GIN indexes for fast querying. This eliminates the need for ALTER TABLE migrations entirely.
3. ADD a read-optimized layer (Elasticsearch or Redis) for the product search/browse experience, populated via CDC (Change Data Capture) from PostgreSQL.
4. RESERVE MongoDB only if a genuinely document-native use case emerges (e.g., user activity logs, session data) where ACID is not required.

This gives us: relational integrity where it matters (money), schema flexibility where it's needed (products), and read performance where users feel it (search).`,
  
  scores: {
    logicalConsistency: 0.90,
    deductiveValidity: 0.80,
    informationEfficiency: 0.75,
    coherence: 0.85
  }
});

// ============================================================
// PHASE 4: STRESSTEST
// ============================================================
phase('PHASE 4: STRESSTEST — Edge Cases & Pre-Mortem', {
  phase: 'stresstest',
  content: `The polyglot persistence approach is robust but introduces operational complexity. The CDC pipeline between PostgreSQL and Elasticsearch is a new failure point. If it lags, search results become stale. However, this is a much safer failure mode than losing ACID on financial transactions.`,
  
  confidence: 0.92,
  
  premortem: `The system failed in 12 months because the CDC pipeline between PostgreSQL and Elasticsearch became the weakest link. During Black Friday, the pipeline lagged 45 minutes behind, causing customers to see "in stock" for items that were sold out. The team tried to fix it by adding more Kafka partitions, but the real issue was that the Elasticsearch mapping was too complex and reindexing took hours. Meanwhile, the JSONB product catalog in PostgreSQL grew to 500GB and GIN index rebuilds started taking 30+ minutes, blocking deployments. The team regretted not investing in a proper product information management (PIM) system from the start.`,
  
  stressResults: [
    {
      scenario: 'Black Friday: 50x traffic spike on product pages',
      outcome: 'pass',
      risk: 'medium',
      detail: 'Elasticsearch handles read scaling independently. PostgreSQL only handles orders (much lower volume).'
    },
    {
      scenario: 'New product type added with 20 unique attributes',
      outcome: 'pass',
      risk: 'low',
      detail: 'JSONB column absorbs any attribute schema without migration. GIN index auto-covers new keys.'
    },
    {
      scenario: 'CDC pipeline fails during peak hours',
      outcome: 'partial',
      risk: 'high',
      detail: 'Search results become stale but orders/payments continue working. Degraded but not broken.'
    },
    {
      scenario: 'Need to join product data with order analytics for reporting',
      outcome: 'pass',
      risk: 'medium',
      detail: 'All data lives in PostgreSQL — standard SQL JOINs work. No cross-database query needed.'
    },
    {
      scenario: 'Team member who built the CDC pipeline leaves the company',
      outcome: 'fail',
      risk: 'high',
      detail: 'CDC pipelines are complex infrastructure. Knowledge transfer is critical but often neglected. Single point of failure in team knowledge.'
    }
  ]
});

console.log('\n' + '═'.repeat(60));
console.log('SESSION COMPLETE');
console.log('═'.repeat(60));
