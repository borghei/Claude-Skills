import React, { useState } from "react";
import { cn } from "./cn";

type Invoice = { id: string; client: string; amount: string; daysOverdue: number };

export function InvoiceRow({ invoice, onRemind }: { invoice: Invoice; onRemind: (id: string) => void }) {
  const [sending, setSending] = useState<boolean>(false);
  return (
    <tr className="border-b border-slate-200">
      <td className="py-2 pr-3 text-slate-900">{invoice.client}</td>
      <td className="py-2 pr-3 text-slate-600">{invoice.id}</td>
      <td className="py-2 pr-3 text-right tabular-nums text-slate-900">{invoice.amount}</td>
      <td className="py-2 pr-3">
        <span className="text-sm font-semibold text-red-700">Overdue {invoice.daysOverdue} days</span>
      </td>
      <td className="py-2">
        <button
          type="button"
          className={cn(
            "rounded-md bg-blue-700 px-3 py-1.5 text-sm text-white motion-safe:transition-colors",
            "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2",
            sending && "opacity-60"
          )}
          disabled={sending}
          onClick={() => {
            setSending(true);
            onRemind(invoice.id);
          }}
        >
          {sending ? "Sending reminder" : "Send reminder"}
        </button>
      </td>
    </tr>
  );
}
