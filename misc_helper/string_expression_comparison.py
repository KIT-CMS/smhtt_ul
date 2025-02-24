# Created with assistance of Copilot (o3-mini)

import re
import random
from array import array
import ROOT

from pyparsing import (
    Word,
    alphas,
    alphanums,
    nums,
    oneOf,
    Literal,
    Combine,
    Optional,
    Forward,
    Group,
    delimitedList,
    infixNotation,
    opAssoc,
    ParserElement,
)  # Pyparsing-based parser for C++-like expressions
ParserElement.enablePackrat()

# Basic tokens.
identifier = Word(alphas + "_", alphanums + "_")
number = Combine(Optional(oneOf("+ -")) + (Word(nums) + Optional("." + Word(nums)) | ("." + Word(nums))))
number.setParseAction(lambda t: float(t[0]))

expr = Forward()  # New grammar additions for function calls
arg_list = Optional(delimitedList(expr))  # comma-separated list for function arguments.

# A function call: identifier '(' [expr, ...] ')'
function_call = Group(identifier("func") + Literal("(").suppress() + arg_list("args") + Literal(")").suppress())
# Changed parse action so the function name is preserved.
function_call.setParseAction(lambda t: (t[0], tuple(t[1:])))
atom = function_call | number | identifier  # operand: callable, number, or identifier.

# Build the grammar using infixNotation on the new atom.
expr << infixNotation(
    atom,
    [
        ((Literal("!") | Literal("+") | Literal("-")), 1, opAssoc.RIGHT),  # Unary operators: NOT, plus, minus.
        (oneOf("* /"), 2, opAssoc.LEFT),  # Multiplicative: * and /
        (oneOf("+ -"), 2, opAssoc.LEFT),  # Additive: + and -
        (oneOf("== != > < >= <="), 2, opAssoc.LEFT),  # Comparison: ==, !=, >, <, >=, <=.
        (Literal("&&"), 2, opAssoc.LEFT),  # Logical AND.
        (Literal("||"), 2, opAssoc.LEFT),  # Logical OR.
    ],
)


def _parse_expr(expr_str: str) -> list:
    """
    Parse the selection expression into a nested structure (AST).
    """
    return expr.parseString(expr_str, parseAll=True).asList()[0]  # nested structure (AST)


def _normalize(ast: list) -> tuple:
    """
    Recursively normalize the AST:
      - Flatten extraneous nesting.
      - Convert numbers so that 10 and 10.0 compare equal.
      - Apply special rules for binary comparisons.
      - For logical AND/OR, flatten order-independent operands using a frozenset.
      - Remove spurious empty-string tokens.
      - Simplify function call ParseResults.
    """
    def flatten_chain(node, op):
        # If node is a canonical chain (already flattened as (op, frozenset(...))),
        # then recursively flatten its operands.
        if isinstance(node, tuple) and len(node) == 2 and node[0] == op and isinstance(node[1], frozenset):
            flattened = []
            for sub in node[1]:
                flattened.extend(flatten_chain(sub, op))
            return flattened
        # If node is a binary chain (a tuple of length 3 with middle element op)
        if isinstance(node, tuple) and len(node) == 3 and node[1] == op:
            return flatten_chain(node[0], op) + flatten_chain(node[2], op)
        return [node]

    # Convert ParseResults to list if needed.
    if hasattr(ast, "asList"):
        ast = ast.asList()
    # Simplify function call nodes:
    if isinstance(ast, tuple) and len(ast) == 2 and ast[1] == () and hasattr(ast[0], "asList"):
        inner = ast[0].asList()
        return (inner[0],) + tuple(_normalize(x) for x in inner[1:])
    if isinstance(ast, list):
        # Remove empty-string tokens (from extra parentheses)
        ast = [x for x in ast if x != ""]
        if len(ast) == 1:
            return _normalize(ast[0])
        # Handle unary operators.
        if len(ast) == 2 and isinstance(ast[0], str) and ast[0] in ("!", "+", "-"):
            return (ast[0], _normalize(ast[1]))
        norm_items = [_normalize(item) for item in ast]
        # Special handling for binary comparisons.
        if (len(norm_items) == 3 and isinstance(norm_items[1], str) and
                norm_items[1] in (">", "<", ">=", "<=", "==", "!=")):
            left, op, right = norm_items
            if op == ">" and isinstance(right, float) and abs(right - 0.5) < 1e-8:
                op, right = "==", 1.0
            elif op == "<" and isinstance(right, float) and abs(right - 0.5) < 1e-8:
                op, right = "==", 0.0
            if op in ("<", ">") and isinstance(left, float) and not isinstance(right, float):
                left, right = right, left
                op = ">" if op == "<" else "<"
            return (left, op, right)
        result = tuple(norm_items)
        # If result is a logical chain (odd-length tuple with same operator in odd indices)
        if isinstance(result, tuple) and len(result) >= 3 and (len(result) % 2 == 1):
            op = result[1]
            if all(result[i] == op for i in range(1, len(result), 2)) and op in ("&&", "||"):
                operands = []
                # Flatten both left and right parts recursively.
                for i in range(0, len(result), 2):
                    operands.extend(flatten_chain(result[i], op))
                return (op, frozenset(operands))
        return result
    return ast


def check_structure_equivalence(expr1: str, expr2: str, verbose=False) -> bool:
    """
    Check that the two expressions have the same structure:
    They must parse to normalized ASTs with identical variable (identifier) usage.
    """
    try:
        ast1, ast2 = _normalize(_parse_expr(expr1)), _normalize(_parse_expr(expr2))
    except Exception as e:
        print("Parsing error:", e)
        return False
    _print = print if verbose else lambda *args, **kwargs: None
    # Print normalized ASTs for debugging purposes.
    _print("Normalized Expression 1:", ast1)
    _print("Normalized Expression 2:", ast2)
    return ast1 == ast2


# --- ROOT TFormula evaluation functions ---
def _extract_variables(expr: str) -> list:
    """
    Extract identifier names from the expression.
    Excludes common C++ operators, keywords and built‐in functions available
    in ROOT (such as abs, pow, sqrt, exp, log).
    """
    tokens = set(re.findall(r'\b[a-zA-Z_]\w*\b', expr))
    # Do not treat ROOT built-in functions as variables.
    keywords = {"abs", "pow", "sqrt", "exp", "log"}
    return sorted(token for token in tokens if token not in keywords)


def _transform_expr(expr: str, mapping: dict[str, int]) -> str:
    """
    Replace each variable in mapping with its TFormula parameter notation.
    For example, if mapping = {"pt": 0, "IsoMu22": 1}, then the expression
    "pt>20 && IsoMu22==1" becomes "[0]>20 && [1]==1".
    IMPORTANT: Variables that are in the ROOT built-ins (e.g. abs, pow, etc.)
    are not replaced.
    """
    new_expr = expr
    # A set of keywords that should not be transformed.
    keywords = {"abs", "pow", "sqrt", "exp", "log"}
    for var, idx in mapping.items():
        if var in keywords:
            continue
        new_expr = re.sub(rf"\b{var}\b", f"[{idx}]", new_expr)
    return new_expr


def _evaluate_formula(expr: str, mapping: dict[str, int], values: list) -> float:
    """
    Create a TFormula from the transformed expression and evaluate it.
    'values' must be a list of floats corresponding to the parameters.
    """
    transformed = _transform_expr(expr, mapping)
    f = ROOT.TFormula("f", transformed)
    vals_array = array('d', values)
    return f.EvalPar(vals_array, 0)


def check_evaluation_equivalence(
    expr1: str,
    expr2: str,
    tol: float = 1e-8,
    verbose: bool = False,
) -> bool:
    """
    Check if two expressions produce the same output using ROOT's TFormula.
    Instead of using random test values, this version scans both expressions for
    logical comparisons. For each comparison, candidate values for the involved
    variable are generated (for example, for 'pt > 20', the candidates are 19, 20, 21).
    For equality checks of integer constants (e.g. gen_tau == 2), candidates are chosen
    as {value-1, value, value+1} (and for the special case of IsoMu==1, the candidates are {0,1}).
    Variables not appearing in a comparison are tested with a default value (0.0).
    """
    import re
    from itertools import product

    # Get all variables used by both expressions.
    all_vars = sorted(set(_extract_variables(expr1)) | set(_extract_variables(expr2)))
    mapping = {var: i for i, var in enumerate(all_vars)}

    # Build candidate sets from comparisons, default to empty set.
    candidates = {var: set() for var in all_vars}

    # Regex to extract comparisons of the form: variable [operator] number.
    pattern = re.compile(r'\b([a-zA-Z_]\w*)\s*(==|>|<|>=|<=|!=)\s*([0-9]+(?:\.[0-9]+)?)')
    for expr in (expr1, expr2):
        for m in pattern.finditer(expr):
            var, op, num_str = m.groups()
            value = float(num_str)
            # Special case: if the constant is near 0.5, then use {0,1}.
            if abs(value - 0.5) < 1e-8:
                new_candidates = {0.0, 1.0}
            elif op in (">", "<", ">=", "<="):
                new_candidates = {value - 0.1, value, value + 0.1}
            elif op in ("==", "!="):
                # Special handling for equality: do not modify candidates.
                if abs(value - 1) < 1e-8:
                    new_candidates = {0.0, 1.0}
                elif value.is_integer() and value > 1:
                    new_candidates = {value - 1, value, value + 1}
                else:
                    new_candidates = {value}
            else:
                new_candidates = {value}
            if var in candidates:
                candidates[var].update(new_candidates)
            else:
                candidates[var] = new_candidates

    # For variables with no candidate from comparisons, set a default value.
    for var in all_vars:
        if not candidates[var]:
            candidates[var].add(0.0)

    # Compute the cartesian product for all candidate test values.
    candidate_values = [sorted(candidates[var]) for var in all_vars]
    test_vectors = list(product(*candidate_values))

    _print = print if verbose else lambda *args, **kwargs: None

    for test_vals in test_vectors:
        try:
            val1 = _evaluate_formula(expr1, mapping, list(test_vals))
            val2 = _evaluate_formula(expr2, mapping, list(test_vals))
        except Exception as e:
            _print("Error evaluating expressions:", e)
            return False
        if abs(val1 - val2) > tol:
            _print("Test vector", dict(zip(all_vars, test_vals)), "failed evaluation equivalence")
            return False
    return True


def check_logical_equivalence(
    expr1: str,
    expr2: str,
    n_tests: int = 100,
    tol: float = 1e-8,
    verbose: bool = False,
) -> bool:
    """
    Check if two C++-style selection expression strings are logically equivalent.
    This function first checks that the expressions have the same structure
    (i.e. the same variable names appear in the same logical positions) and then
    uses ROOT's TFormula to compare their outputs via random testing.
    Note: Sampling cannot guarantee full equivalence, but is a practical test.
    """
    _print = print if verbose else lambda *args, **kwargs: None
    _print("=== Structure Check ===")
    if not check_structure_equivalence(expr1, expr2):
        _print("Structure equivalence FAILED")
        return False
    _print("Structure equivalence PASSED")

    _print("=== Evaluation Check ===")
    if not check_evaluation_equivalence(expr1, expr2, tol=tol):
        _print("Evaluation equivalence FAILED")
        return False
    _print("Evaluation equivalence PASSED")

    return True
