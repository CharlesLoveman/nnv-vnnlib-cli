import argparse
import os
import subprocess
import pathlib

import matlab.engine

eng = None


def get_engine() -> matlab.engine.MatlabEngine:
    global eng
    if eng is None:
        eng = matlab.engine.start_matlab()
        eng.addpath(os.getcwd())

        nnv_root = os.environ.get("NNV_ROOT")
        if not nnv_root:
            here = os.path.dirname(os.path.abspath(__file__))
            nnv_root = os.path.abspath(os.path.join(here, "..", ".."))
        eng.addpath(eng.genpath(nnv_root))
    return eng


def get_version() -> str:
    eng = get_engine()
    return eng.NNVVERSION().split(" ")[1]


def get_name() -> str:
    eng = get_engine()
    return eng.NNVVERSION().split(" ")[0]


def verify(filepath: str, networks: dict[str, str], **kwargs) -> tuple[str, str]:
    eng = get_engine()
    print(networks)
    for network, network_path in networks.items():
        path = pathlib.Path(network_path)
        network_filetype = path.suffix.lower()
        if network_filetype == ".onnx":
            subprocess.run(
                [
                    "python",
                    "../../tools/onnx2nnv_python/onnx2nnv.py",
                    network_path,
                    path.with_suffix(".mat").absolute().as_posix(),
                    "--vnnlib",
                    filepath,
                ],
                check=True,
            )
        elif network_filetype == ".mat":
            pass
        else:
            raise ValueError(f"Unsupported network file type: {network_filetype}")
        networks[network] = path.with_suffix(".mat").absolute().as_posix()
    # need to handle timeout
    result, witness = eng.run_vnnlib_query(
        filepath, matlab.dictionary(networks), kwargs, nargout=2
    )
    map = ["sat", "unsat", "unknown"]
    return map[int(result)], witness


def get_onnx_opset_versions() -> tuple[str, str]:
    return ("0.0", "0.0")


def get_onnx_element_types() -> list[str]:
    return []


def get_onnx_operators() -> list[str]:
    return []


def get_vnnlib_versions() -> tuple[str, str]:
    return ("2.0", "2.0")


def get_hidden_node_theories() -> list[str]:
    return []


def get_multiple_input_output_theories() -> list[str]:
    return []


def get_multiple_network_theories() -> list[str]:
    return []


def get_multiple_node_comparison_theories() -> list[str]:
    return []


def get_arithmetic_complexity_theories() -> list[str]:
    return []


def get_optimised_disjunctive_reasoning() -> bool:
    return False


def get_serialise_assignments() -> bool:
    return False


parser = argparse.ArgumentParser(description="VNN-LIB 2.0 CLI")

# Global options
parser.add_argument(
    "--name", action="store_true", help="Display the name of the solver"
)
parser.add_argument(
    "--version", action="store_true", help="Display the version of the solver"
)

# Commands (verify / capabilities)
subparsers = parser.add_subparsers(dest="command", help="Command")

verify_parser = subparsers.add_parser("verify", help="Verify VNN-LIB query")
verify_parser.add_argument("filepath", type=str, help="Path to the VNN-LIB query file")
verify_parser.add_argument(
    "--network", action="append", default=[], help="<name>=<filepath>"
)
verify_parser.add_argument("--timeout", type=int, help="Timeout in seconds")
verify_parser.add_argument(
    "--serialise-assignments", action="store_true", help="Serialise assignments"
)


supports_parser = subparsers.add_parser("supports", help="Check capabilities")

supports_parser.add_argument(
    "--onnx-opset-versions",
    action="store_true",
    help="Prints a newline-separated pair of the minimum and maximum ONNX opset versions that the solver supports.",
)
supports_parser.add_argument(
    "--onnx-element-types",
    action="store_true",
    help="Prints a newline-separated list of the element types that the solver supports.",
)
supports_parser.add_argument(
    "--onnx-operators",
    action="store_true",
    help="Reports the ONNX operators (e.g., Conv, Relu, Gemm) that are supported by the solver.",
)

supports_parser.add_argument(
    "--vnnlib-versions",
    action="store_true",
    help="Prints a newline-separated pair of the minimum and maximum versions (inclusive) of VNN-LIB that the solver supports.",
)
supports_parser.add_argument(
    "--hidden-node-theories",
    action="store_true",
    help="Which of the Hidden Noes theories described in Section 4.1.1 does the solver support?.",
)
supports_parser.add_argument(
    "--multiple-input-output-theories",
    action="store_true",
    help="Which of the Multiple Inputs/Outputs theories described in Section 4.1.2 does the solver support?",
)
supports_parser.add_argument(
    "--multiple-network-theories",
    action="store_true",
    help="Which of the Multiple Networks theories described in Section 4.1.3 does the solver support?",
)
supports_parser.add_argument(
    "--multiple-node-comparison-theories",
    action="store_true",
    help="Which of the Multiple Node Comparisons theories described in Section 4.1.4 does the solver support?",
)
supports_parser.add_argument(
    "--arithmetic-complexity-theories",
    action="store_true",
    help="Which of the Arithmetic Complexity theories described in Section 4.1.5 does the solver support?",
)
supports_parser.add_argument(
    "--optimised-disjunctive-reasoning",
    action="store_true",
    help="Does the solver use an intelligent strategy for handling queries involving (or ...) statements or simply translates them to disjunctive normal form? If the latter, then higher-level tools can use this flag to decide whether to perform the conversion to DNF themselves and hence get a better indication of progress.",
)

supports_parser.add_argument(
    "--serialise-assignments",
    action="store_true",
    help="Does the solver support the –serialise-assignments option to the verify command?",
)


args = parser.parse_args()
if args.name:
    print(get_name())
if args.version:
    print(get_version())

if args.command == "verify":
    # check file exists
    # get networks
    # handle serialise-assignments
    networks = {}
    for network_assignment in args.network:
        [name, network_file] = network_assignment.split("=")
        networks[name] = network_file
    result, witness = verify(
        args.filepath,
        networks=networks,
        opts={
            "serialise_assignments": args.serialise_assignments,
        },
    )
    print(result)
    if result == "sat":
        print(witness)


elif args.command == "supports":
    if args.onnx_opset_versions:
        print("{}\n{}".format(*get_onnx_opset_versions()))
    if args.onnx_element_types:
        print("\n".join(get_onnx_element_types()))
    if args.onnx_operators:
        print("\n".join(get_onnx_operators()))
    if args.vnnlib_versions:
        print("{}\n{}".format(*get_vnnlib_versions()))
    if args.hidden_node_theories:
        print("\n".join(get_hidden_node_theories()))
    if args.multiple_input_output_theories:
        print("\n".join(get_multiple_input_output_theories()))
    if args.multiple_network_theories:
        print("\n".join(get_multiple_network_theories()))
    if args.multiple_node_comparison_theories:
        print("\n".join(get_multiple_node_comparison_theories()))
    if args.arithmetic_complexity_theories:
        print("\n".join(get_arithmetic_complexity_theories()))
    if args.optimised_disjunctive_reasoning:
        print(str(get_optimised_disjunctive_reasoning()).lower())
    if args.serialise_assignments:
        print(str(get_serialise_assignments()).lower())
