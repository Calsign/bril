#!/usr/bin/env python3

import sys
import json
import subprocess


def recover_traces(source):
    prog = json.loads(subprocess.run(f'cat {source} | bril2json',
                                     shell=True, capture_output=True).stdout.decode('utf-8'))

    # tbh this is not good code

    fresh_label_counter = 0

    def fresh_label():
        fresh_label_counter += 1
        return '_fresh_' + str(fresh_label_counter)

    # PCs of instructions that we have inserted in the middle of the function
    added_instr_pcs = {}
    # labels that we have traced in a function
    traced_labels = {}

    def added_instrs_before(func_name, pc):
        if func_name in added_instr_pcs:
            return len(filter(lambda _pc: _pc <= pc, added_instr_pcs[func_name]))
        else:
            return 0

    def add_instr(func_name, pc):
        if func_name in added_instr_pcs:
            added_instr_pcs[func_name].append(pc)
        else:
            added_instr_pcs[func_name] = [pc]

    def add_traced_label(func_name, label):
        if func_name in traced_labels:
            traced_labels[func_name].append(label)
        else:
            traced_labels[func_name] = [label]

    def traced_label_name(label):
        return "_" + label + "_traced"

    for line in sys.stdin:
        instr = json.loads(line)

        if instr['op'] == 'speculate':
            func_name = instr['args'][0]
            for _func in prog['functions']:
                if func_name == _func['name']:
                    func = _func
                    break
            else:
                raise Exception(f'Could not find function: {func_name}')

            header_pc = instr['args'][1]
            header_label = instr['labels'][0]
            del instr['labels']
            del instr['args']

            add_traced_label(func_name, header_label)

            func['instrs'].append({'label': traced_label_name(header_label)})

        func['instrs'].append(instr)

        if instr['op'] == 'commit':
            if 'labels' in instr:
                target_label = instr['labels'][0]
                del instr['labels']

                func['instrs'].append({'op': 'jmp', 'labels': [target_label]})

            elif 'args' in instr:
                target_pc = instr['args'][0]
                del instr['args']

                # inject a new label to jump to
                target_label = fresh_label()
                func['instrs'].insert(
                    target_pc + added_instrs_before(func_name, target_pc), {'label': target_label})
                add_instr(func_name, target_pc)

                func['instrs'].append({'op': 'jmp', 'labels': [target_label]})

    for _func in prog['functions']:
        for _instr in _func['instrs']:
            if 'labels' in _instr and _instr['op'] != 'guard':
                for i, _label in enumerate(_instr['labels']):
                    if _label in traced_labels[_func['name']]:
                        _instr['labels'][i] = traced_label_name(_label)

    print(json.dumps(prog))


if __name__ == '__main__':
    # output from tracing is fed in over stdin
    # two arguments: first is source file
    recover_traces(*sys.argv[1:])
