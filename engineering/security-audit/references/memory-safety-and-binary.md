# Memory Safety and Binary Companion

Tier: full.

## Select this companion when

The target contains code where the language does not enforce memory safety or
where bytes are interpreted as structure: C and C++, `unsafe` Rust, manual
memory management in any language, parsers and decoders for untrusted
formats, foreign-function boundaries, binary loaders, just-in-time compilers,
firmware, and kernel or driver interfaces.

Select it for a boundary reconnaissance found — a parser fed from the network,
an FFI call taking caller-sized buffers — not because a native dependency
appears in a manifest.

## Ground rules

```text
- Start from attacker-controlled bytes or sizes and follow them to an
  allocation, an index, a copy, a cast, or a free.
- Report the effect you observed and no more: an out-of-bounds read of N
  bytes, a write past a buffer, a use after free, a crash. Do not claim code
  execution from a crash, and do not build an exploit.
- A sanitizer report or a failing assertion from a bounded local run is good
  evidence. Record the exact input and the tool output.
- Undefined behaviour that only the calling program can trigger against
  itself is a robustness bug, not a boundary failure. Identify who supplies
  the input and whose memory or process is affected.
- Compiler flags, allocator hardening, and platform mitigations reduce
  likelihood; they do not make the defect disappear. Note them, do not rely
  on them.
- Run fuzzers and harnesses only inside the confirmed sandbox, with small
  time and memory limits. A few seconds of targeted input is the goal, not a
  campaign.
```

## Hunting classes

### Out-of-bounds read or write

An index, offset, or length derived from input is used without a check
against the real size, or the check and the use disagree. Look at loop
bounds, off-by-one at terminators, lengths read from the data itself, and
reads that return adjacent memory to the caller.

### Integer overflow, truncation, and signedness

Arithmetic on sizes that wraps before allocation or comparison, narrowing
conversions that drop high bits, signed values compared as unsigned or the
reverse, and negative lengths passed to routines expecting sizes.

### Unit and size confusion

Bytes mixed with elements, characters with code units, a count used as a
byte length, a size of a pointer used for a size of its target, or a length
that includes a terminator in one place and not another.

### Uninitialized memory disclosure

Stack or heap memory returned, serialized, or sent before being fully
written: padding in structures, partially filled buffers, error paths that
skip initialization.

### Use after free and double free

An object released while another reference, iterator, callback, or view still
points at it; cleanup paths that free twice; containers resized while a
pointer into them is held; lifetimes that depend on callback ordering.

### Type confusion

Memory treated as a type it is not: unchecked downcasts, tagged unions read
with the wrong tag, deserialized type identifiers trusted, variant objects
whose tag and payload can be changed separately.

### Reference count and ownership races

Counts incremented or decremented without synchronization, a borrowed
reference used after the owner released it, and ownership transferred across
threads or callbacks with no clear rule.

### Data races and check-then-use

Shared state read and acted on without holding the lock that protects it; a
value validated and then re-read; file or object identity checked and then
reopened by name.

### Deadlock and lock ordering

Locks taken in inconsistent order, a lock held across a callback or blocking
call that input can stall, and recursive paths that re-acquire. Report as an
availability effect on whoever shares the process.

### FFI length and ownership contracts

Each side of a foreign call believes something different about who allocates,
who frees, how long a pointer is valid, or how large a buffer is. Read the
declaration on both sides and the wrapper between them.

### Layout, alignment, and enum mismatch

Structures declared differently across languages or compilation units,
packing and alignment assumptions, and enum values outside the range the
receiving side handles.

### Unwinding across a foreign boundary

Exceptions or panics that cross into code that cannot handle them, leaving
locks held or state half-updated, and callbacks invoked on a thread the
callee does not expect.

### Library and plugin search order

The process loads a library, plugin, or helper executable by name from a
search path that includes a directory a lower-privilege user can write to.

### Unverified loaded artifacts

Code, modules, or firmware images loaded with no check of signature or
digest, or with a check on one file while a different file is executed.

### Malformed binary metadata

Loaders and format parsers that trust offsets, counts, section sizes, and
relocation entries inside the file: overlapping sections, offsets beyond the
end, counts that overflow when multiplied.

### JIT and generated code consistency

Generated code that assumes a type or bound the runtime can later invalidate,
writable-and-executable regions, and caches of compiled code keyed too
loosely.

### Unload and teardown

Callbacks, timers, or threads that still reference a module or object being
unloaded; shutdown paths that free state other threads are using.

### User-copy bounds and double fetch

Kernel or privileged code copying from a caller: sizes taken from the caller
without a ceiling, a value fetched twice with a check in between, and
structures copied back with uninitialized fields.

### Privileged object lifetime

Handles, descriptors, and kernel objects whose lifetime a caller can race:
closing during an operation, reusing an identifier after release, dispatch
tables indexed by a caller-supplied number.

### Powerful interfaces with weak checks

Device controls, debug interfaces, and management calls that perform
privileged operations and verify only that the caller could open the device.

## Cross-cutting moves

- For every length, find where it comes from, where it is checked, and where
  it is used. All three must agree on unit and type.
- Read error and early-return paths for skipped initialization and double
  cleanup.
- Check the largest and smallest values: zero, one, maximum, maximum plus
  one, negative.
- Follow each allocation to every free and each free to every remaining
  reference.
- Prefer an existing unit test or fuzz target as the harness, with a single
  crafted input.

## Evidence bar

- Confirmed needs a concrete input and an observed effect from a bounded
  local run: a sanitizer report, a failed bounds assertion, or adjacent
  memory in the output.
- If no sandbox or toolchain is available, a fully traced arithmetic or
  lifetime argument stays `needs_validation`, with the missing run as the
  blocker and the exact harness described.
- Severity follows the observed primitive and who reaches it: a remote
  unauthenticated write is high or critical; a bounded read of non-sensitive
  memory is low. Do not rate on what an exploit might achieve.
- Crashes only the caller can inflict on itself are hardening notes.
