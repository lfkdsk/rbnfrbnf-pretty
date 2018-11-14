from .syntax_graph import Node, Identified, SubRoutine, NamedTerminal, UnnamedTerminal, NonTerminalEnd
from .tokenizer import Token, InternedString
from typing import List
from rbnfrbnf import linked_lst


class State:
    tokens: List[Token]
    offset: int


def make_token(s: str, t: int = 0):
    return Token(0, 1, 2, 'sss', t, InternedString(s))


def run_graph(tokens: List[Token], start: Identified):
    offset = 0
    linked_lst_reverse = linked_lst.reverse
    linked_lst_iterate = linked_lst.iterate

    def call_subroutine(identified: Identified):
        nonlocal offset
        histories = (offset, ())
        results = (), ()
        envs = [iter(identified.starts)]
        while envs:
            current = next(envs[-1], None)
            if not current:
                # resume
                envs.pop()
                offset, histories = histories
                try:
                    results = results[1]
                except IndexError:
                    assert not envs
                    return False, None
            ty = type(current)
            if ty is UnnamedTerminal:
                try:
                    token = tokens[offset]
                except IndexError:
                    return True, results

                s1: InternedString = current.value
                s2 = token.value
                if (s2.i is 0 and s1.s == s2.s) or (s2.i == s1.i):
                    histories = offset, histories
                    offset += 1
                    results = (token, results[0]), results
                    envs.append(iter(current.parents))
            elif ty is NamedTerminal:
                try:
                    token = tokens[offset]
                except IndexError:
                    return True, results
                if current.typeid == token.type:
                    histories = offset, histories
                    offset += 1
                    results = (token, results[0]), results
                    envs.append(iter(current.parents))

            elif ty is NonTerminalEnd:
                histories = offset, histories
                result = results[0]
                result = (current.name, *linked_lst_iterate(linked_lst_reverse(result))), ()
                results = result, results
                envs.append(iter(current.parents))

            elif ty is SubRoutine:
                assert isinstance(current, SubRoutine)
                status, sub_results = call_subroutine(current.root)
                if status:
                    histories = offset, histories
                    results = (sub_results, results[0]), results
                    envs.append(iter(current.parents))

        return False, None

    a, b = call_subroutine(start)
    if a:
        return b[0]
    raise Exception
