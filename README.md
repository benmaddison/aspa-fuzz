# aspa-fuzz

This project started out as a tool to use hypothesis testing to verify
equivalence between alternative algorithms for detection of leaked BGP
routes using ASPA.

In the process, however, I have identified various respects in which the
canonical algorithm (from draft-ietf-sidrops-aspa-verification-06) produces
suboptimal (or downright incorrect) results.

These are documented below.

## Installation and Usage

This project consists of a python library implementing the verification
procedure for ASPA, and an associated suite of tests.

Whilst this library can be installed and used for other purposes, the intention
is for use with the suite of test cases provided in `test/`.

To run the tests locally:
``` bash
# clone the repo locally and change directory into it
$ git clone https://github.com/benmaddison/aspa-fuzz
$ cd aspa-fuzz
# create a new python venv and install tox
$ python -m venv .venv
$ source .venv/bin/activate
$ pip install tox
# execute tox to run the tests
$ tox
```

`tox` will take care of creating a testing environment, installing the `aspa` library
and the other test dependencies into it, and then executing `py.test` to run the tests.

## Test cases

The test behaviour is defined in two files:
- `test/aspa_set.yml`:
  defines the set of ASPA object payloads that should be considered during validation.
- `test/test_cases.yml`:
  defines the set of tests that should be expected. These take the form of a description
  of the relevant BGP route/neighbor attributes, and the expected outcome of the validation
  procedure.

The schema of each of these files should be self-explanatory.

Each test case defined will be executed for all implemented verification algorithm, and for
both IPv4 and IPv6 AFIs.

## Verification Algorithms

The available implementations each present a consistent API to facilitate easy test case
construction. However, they each differ in the arguments that they consider relevant at
runtime.

Care should be taken when writing test cases so that the test is performed in a semantically
equivalent manner.

- `Draft6Validator` is the implementation defined in draft-ietf-sidrops-aspa-verification-06.
  Where the draft provides example python code, this has been incorporated (almost) verbatim.

  The `Draft6Validator` does not attempt to infer whether the neighbor from which a path is
  received should be treated as a "Provider" (i.e. a neighboring AS from which to expect downstream
  transit announcement) or not.
  Instead the neighbor type and ASN are explicitly passed as arguments to the `.validate()` call,
  and different logic is used for the provider/non-provider cases.

  See `aspa/neighbors.py` for the list of allowed neighbor types.

- `HeitzValidator` is an implementation of the algorithm described by Jakob Heitz in [1].

  The `HeitzValidator`, by comparison, makes use of the `local_as` argument to the class constructor
  in order to consider the path with the receiver ASN appended. The validator is thus able to
  consider ASPA objects created by the receiver AS when determining whether downstream transit
  announcements are valid.

  The `HeitzValidator` is also less opinionated about concerns that (arguably) fall outside the
  scope of leaked path detection, e.g. whether the neighbor ASN matches the last `AS_PATH` component,
  and whether an empty `AS_PATH` can be Valid.

### Comparison

Behaviour | `Draft6Validator` | `HeitzValidator`
----------|-------------------|-----------------
Empty `AS_PATH` | Always `Invalid` | Always `Valid`
Provider identification | Explicit | Uses ASPA objects
Neighbor AS mismatch | `Invalid` unless `neighbor_type=IxpRouteServer` | Not considered
