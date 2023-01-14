from ast import *
import ast
from functools import reduce
from operator import add
import pathlib
from dataclasses import dataclass


def todo(a: AST):
    return NotImplementedError(a, dump(a, indent=4))

@dataclass
class Transformer:
    file: str

    def transform(self):
        with open(self.file, "r") as f:
            Tree = parse(
                f.read(), pathlib.Path(self.file).name, mode="exec", type_comments=True
            )
            Tree = MacthStmtTransformer().visit(Tree)
            fix_missing_locations(Tree)
            return unparse(Tree)


class MacthStmtTransformer(ast.NodeTransformer):
    def visit_Match(self, node):
        match node:
            case ast.Match(subject, cases):
                return recurse_transform(subject, cases)
            case _:
                return node


def recurse_transform(subject, rest_cases):
    case, *rest_cases = rest_cases
    orelse = [recurse_transform(subject, rest_cases)] if rest_cases else []
    match case:
        case match_case(patt, None, body):

            def deepparse(stmt):
                subTree = MacthStmtTransformer().visit(stmt)
                # fix_missing_locations(subTree)
                return subTree

            return match_pattern0(
                subject=subject,
                orelse=orelse,
                patt=patt,
                body=list(map(deepparse, body)),
            )
        case _:
            raise todo(case)


def match_pattern0(subject, orelse, patt, body):
    match patt:
        case MatchSingleton(value):
            return If(
                test=Compare(
                    left=subject, ops=[Is()], comparators=[Constant(value=value)]
                ),
                body=body,
                orelse=orelse,
            )

        case MatchValue(value):
            match value:
                case Constant(value) as const:
                    return If(
                        test=Compare(left=subject, ops=[Eq()], comparators=[const]),
                        body=body,
                        orelse=orelse,
                    )
                case _:
                    raise todo(value)

        case MatchClass(cls, patterns, kwd_attrs, kwd_patterns):
            targets = []
            elts = []
            test = Compare(
                left=Call(
                    func=Name(id="isinstance", ctx=Load()),
                    args=[subject, cls],
                    keywords=[],
                ),
                ops=[],
                comparators=[],
            )

            match patterns, kwd_attrs, kwd_patterns:
                case pats, [], []:

                    def handle_pattern(i, patt):
                        subject_value = Subscript(
                            value=Attribute(
                                value=cls,
                                attr="__dataclass_fields__",
                                ctx=Load(),
                            ),
                            slice=Constant(value=i),
                            ctx=Load(),
                        )
                        
                        # Call(
                        #         Name(id="list", ctx=Load()),
                        #         keywords=[],
                        #         args=[
                        #             Attribute(
                        #                 value=cls,
                        #                 attr="__dataclass_fields__",
                        #                 ctx=Load(),
                        #             )
                        #         ],
                        #     ),

                        nonlocal test
                        match patt:
                            case MatchAs(pattern=None, name=name):
                                targets.append(Name(id=name, ctx=Store()))
                                elts.append(
                                    Call(
                                        func=Attribute(
                                            value=subject,
                                            attr="__getattribute__",
                                            ctx=Load(),
                                        ),
                                        args=[subject_value],
                                        keywords=[],
                                    )
                                )
                            case MatchValue(value):
                                test = BoolOp(
                                    op=And(),
                                    values=[
                                        test,
                                        Compare(
                                            left=subject_value,
                                            ops=[Eq()],
                                            comparators=[value],
                                        ),
                                    ],
                                )
                            case _:
                                todo(patt)

                    for i, p in enumerate(pats):
                        handle_pattern(i, p)

                    return If(
                        test=test,
                        body=(
                            [
                                Assign(
                                    targets=[Tuple(elts=targets, ctx=Store())],
                                    value=Tuple(elts=elts),
                                    ctx=Load(),
                                )
                            ]
                            if len(targets)
                            else []
                        )
                        + (body),
                        orelse=orelse,
                    )

                case [], kas, kps:

                    def handle_pattern(ka, patt):
                        nonlocal test

                        subject_value = Attribute(
                            value=subject,
                            attr=ka,
                            ctx=Load(),
                        )

                        match patt:
                            case MatchAs(pattern=None, name=name):
                                targets.append(Name(id=name, ctx=Store()))
                                elts.append(subject_value)

                            case MatchValue(value):
                                test = BoolOp(
                                    op=And(),
                                    values=[
                                        test,
                                        Compare(
                                            left=subject_value,
                                            ops=[Eq()],
                                            comparators=[value],
                                        ),
                                    ],
                                )
                            case _:
                                todo(patt)

                    zipped = list(zip(kas, kps))

                    for ka, kp in zipped:
                        handle_pattern(ka, kp)

                    return If(
                        test=test,
                        body=(
                            [
                                Assign(
                                    targets=[Tuple(elts=targets, ctx=Store())],
                                    value=Tuple(
                                        elts=elts,
                                        ctx=Load(),
                                    ),
                                )
                            ]
                            if len(targets)
                            else []
                        )
                        + body,
                        orelse=orelse,
                    )

                case _:
                    raise todo(patt)

        case MatchSequence(patterns):
            
            def merge_ifs(ifs: list[If]):
                return If(
                    test=reduce(
                        lambda a, b: BoolOp(op=And(), values=[a, b]),
                        [_.test for _ in ifs if isinstance(_, If)],
                    ),
                    body=list(
                        reduce(add, [_.body if isinstance(_, If) else _ for _ in ifs])
                    )
                    + body,
                    orelse=orelse,
                )

            match patterns:
                case []:
                    return If(
                        test=Compare(
                            left=subject,
                            ops=[Eq()],
                            comparators=[List(elts=[], ctx=Load())],
                        ),
                        body=body,
                        orelse=orelse,
                    )
                case _:

                    def get_new_subject(i):
                        if isinstance(subject, Tuple):
                            print(subject.elts)
                            return subject.elts[i]
                        else:
                            return Subscript(
                                ctx=Load(), slice=Constant(value=i), value=subject
                            )

                    return merge_ifs(
                        [
                            match_pattern0(
                                subject=get_new_subject(i),
                                orelse=orelse,
                                patt=_,
                                body=[],
                            )
                            for i, _ in enumerate(patterns)
                        ]
                    )

        case MatchAs(pattern=patt, name=name):
            match patt, name:
                case None, None:
                    return body
                case None, name:
                    return [
                        Assign(
                            targets=[Name(id=name, ctx=Store())],
                            value=subject,
                        )
                    ] + body
                case _:
                    body = [
                        Assign(
                            targets=[Name(id=name, ctx=Store())],
                            value=subject,
                        )
                    ] + body
                    return match_pattern0(
                        subject=subject, orelse=orelse, patt=patt, body=body
                    )

        case _:
            raise todo(patt)


if __name__ == "__main__":
    main()
