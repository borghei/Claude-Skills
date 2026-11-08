// Sample application code for flag_audit.py. Four flags read through three SDK shapes.
import { ldClient, flags, getFlag } from "./flags";

export async function renderCheckout(user: { id: string }) {
  const newCheckout = await ldClient.boolVariation("release.new_checkout", user, false);
  const recsOff = flags.isEnabled("ops.recs.kill_switch");
  const banner = getFlag("release.old_banner"); // shipped to 100% long ago
  const tier = getFlag("perm.pro_reports");
  return { newCheckout, recsOff, banner, tier };
}
