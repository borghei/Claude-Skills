// Deliberately flawed route for tenant_config_validator.py: unscoped query, global tenant state.
import { db } from '@/lib/db'
import { projects } from '@/db/schema'

export async function GET() {
  globalThis.currentTenant = 'ws_acme'
  const rows = await db.select().from(projects)
  return Response.json(rows)
}
