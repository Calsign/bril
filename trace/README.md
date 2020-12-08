
CS 6120 Lesson 11. wds68.

My implementation works as follows:
 - Add a flag to brili (-t) to enable tracing
 - When tracing, print to stdout (with `TRACE: ` prefix) to log the
   trace
 - Start tracing at every label that we haven't traced yet
 - Stop tracing when we encounter a label that we've seen on this
   trace before (a cycle)
 - Stop tracing when we encounter an unsupported operation (function
   calls, memory access)
 - Process traces with recover_trace.py
 - Add traces to end of function, with new labels (`[label]_traced`)
 - Guards jump back to the original label
 - Change all branch/jmp instructions to go to the traced label
   instead

I tested with the `pythagorean_triple.bril` benchmark. A traced version of
that benchmark is included (`pythagorean_triple.traced.bril`).

I have not performed any optimizations on the traces, so it is not
expected that the number of executed dynamic instructions be
significantly smaller than the untraced program. That being said, it
would not be difficult to plug pre-written optimizations into my
implementation.

It does not currently work correctly. In testing, the program produces
the correct output, but it executes twice, with several times more
dynamic instructions than the untraced program. I don't know quite
what is going wrong, but I think it is mostly correct.
