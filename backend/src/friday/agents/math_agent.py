from __future__ import annotations

import re
from typing import List, Tuple

from friday.engine.types import Agent, StepEvent
from friday.tools import math_tools


class MathAgent(Agent):
    name = "math"
    description = "Handles arithmetic and simple math expressions."

    def run(self, prompt: str) -> tuple[str, list[StepEvent]]:
        steps: list[StepEvent] = []

        # Very safe parser: support + - * / and parentheses, numbers only.
        expr = prompt.strip()

        # extract candidate expression
        expr = re.sub(r"[^0-9\+\-\*\/\(\)\.\s]", "", expr)
        expr = expr.strip()

        if not expr:
            return ("I couldn't find a math expression to calculate.", steps)

        # Evaluate with a tiny shunting-yard to avoid eval.
        def tokenize(s: str) -> list[str]:
            return re.findall(r"\d+\.\d+|\d+|[\+\-\*\/\(\)]", s)

        prec = {"+": 1, "-": 1, "*": 2, "/": 2}

        def to_rpn(tokens: list[str]) -> list[str]:
            out: list[str] = []
            ops: list[str] = []
            for t in tokens:
                if re.fullmatch(r"\d+\.\d+|\d+", t):
                    out.append(t)
                elif t in prec:
                    while ops and ops[-1] in prec and prec[ops[-1]] >= prec[t]:
                        out.append(ops.pop())
                    ops.append(t)
                elif t == "(":
                    ops.append(t)
                elif t == ")":
                    while ops and ops[-1] != "(":
                        out.append(ops.pop())
                    if ops and ops[-1] == "(":
                        ops.pop()
            while ops:
                out.append(ops.pop())
            return out

        def eval_rpn(rpn: list[str]) -> float:
            st: list[float] = []
            for t in rpn:
                if re.fullmatch(r"\d+\.\d+|\d+", t):
                    st.append(float(t))
                else:
                    b = st.pop()
                    a = st.pop()
                    if t == "+":
                        res = math_tools.add(a, b)
                    elif t == "-":
                        res = math_tools.add(a, -b)
                    elif t == "*":
                        res = math_tools.multiply(a, b)
                    elif t == "/":
                        res = math_tools.divide(a, b)
                    else:
                        raise ValueError("bad op")
                    steps.append(StepEvent(kind="tool", data={"tool": t, "a": a, "b": b, "result": res}))
                    st.append(res)
            return st[-1]

        try:
            tokens = tokenize(expr)
            rpn = to_rpn(tokens)
            result = eval_rpn(rpn)
            # Clean formatting
            if abs(result - int(result)) < 1e-9:
                return (str(int(result)), steps)
            return (str(result), steps)
        except Exception:
            return ("I couldn't calculate that. Try a simpler expression like `12 * (7 + 3)`.", steps)
