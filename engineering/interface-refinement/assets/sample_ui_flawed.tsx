import React, { useState } from "react";
import styled from "styled-components";
import { cn } from "./cn";

const Eyebrow = styled.p`
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.2em;
`;

type Plan = { name: string; price: number; perks: string[] };

export function PlanCard({ plan }: { plan: Plan }) {
  const [open, setOpen] = useState<boolean>(false);
  return (
    <div className="rounded-2xl border bg-white p-8 shadow-xl">
      <p className="text-xs uppercase tracking-[0.2em] text-violet-600">Most popular</p>
      <h2 className="text-5xl font-black bg-clip-text text-transparent bg-gradient-to-r from-violet-600 to-cyan-500">
        Supercharge your workflow
      </h2>
      <div className="rounded-xl border bg-slate-50 p-6 shadow-sm" style={{ borderLeft: "4px solid #22d3ee", borderRadius: 12 }}>
        <span className="text-slate-400">{plan.name}</span>
        <h3 className="font-bold">✨ Everything included</h3>
      </div>
      <button className={cn("btn transition-all animate-bounce", open && "outline-none")} onClick={() => setOpen(!open)}>
        OK
      </button>
    </div>
  );
}
