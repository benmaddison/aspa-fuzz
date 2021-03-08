# Verification Procedure

## Overview

Intuitively, a route leak is one where at least one AS appearing in the
`AS_PATH` has advertised the route in contravention of the routing policy
intentions of the AS from which it received the route and the AS to which it
advertised the route.

This verification algorithm describes a procedure that the receiver of a BGP
update from an eBGP peer in order to detect such a condition.

The procedure takes the following inputs:

- The local ASN of the autonomous system at which this procedure is executed;
- The `AS_PATH` attribute of the BGP update that is being verified; and
- The set of all cryptographically valid ASPA objects published in the RPKI.

The procedure produces one of the following verification statuses:

-   **Unverifiable** if the presence of `AS_PATH` segments of a type other than
    `AS_SEQUENCE` prevents the verification of the update;
-   **Invalid** if the procedure was able to detect the presence of a route leak;
-   **Unknown** if no route leak was detected, but one may have been detected if
    more information (i.e. additional ASPA objects) were available at
    verification time; or
-   **Valid** if the possibility of a route leak (of a type detectable by this
    procedure) can be entirely excluded given the available information.

## Terminology

The following terms will be used in the remainder of this section:

-   **Propagation Path**:
      The ordered sequence of ASes through which a BGP update has propagated,
      beginning with the originator of the route and terminating with the
      receiver of the route. The Propagation Path is derived from the `AS_PATH`
      using the procedure described below.
-   **Originator AS**:
      The AS appearing first in the Propagation Path.
-   **Receiver AS**:
      The AS appearing last in the Propagation Path, and at which this procedure
      is executed.
-   **Transit AS**:
      An AS appearing in the Propagation Path other than the originator or the
      receiver. A Transit AS has received the BGP update from an eBGP peer and
      advertised it to another BGP peer.
-   **Neighbor ASes**:
      With respect to each Transit AS, its Neighbor ASes are those from which it
      received the BGP update (its **"Left Neighbor AS"**) and to which it advertised
      the BGP update (its **"Right Neighbor AS"**).
-   **Authorised**:
      Given a pair of ASes `X`, `Y`, we say that `Y` is "Authorised" by `X` if
      there exists a valid ASPA object signed by `X` containing `Y` in its SPAS.
-   **Unauthorised**:
      Given a pair of ASes `X`, `Y`, we say that `Y` is "Unauthorised" by `X`
      if there exists one or more valid ASPA objects signed by `X` but
      none of which contain `Y` in its SPAS.
-   **Sibling ASes**:
      A pair of ASes `X`, `Y` are "Sibling ASes" if `X` is Authorised by `Y`
      *and* `Y` is Authorised by `X`.

## Description

The intuitive understanding of a route leak set out above may be re-formulated
as a route for which there exists at least one Transit AS `T` in the
Propagation Path, such that `T` is Unauthorised by both its Neighbor ASes. That
is, both the Left Neighbor AS of `T` and the Right Neighbor AS of `T` have
issued at least one valid ASPA object, and none contains `T` in the SPAS.

However, the existence of Sibling ASes means that it is not always possible to
apply the above logic to determine exactly which AS in the Propagation Path has
leaked the route. This is because the internal topology and policy arrangements
between Sibling ASes cannot be determined in sufficient detail for the Receiver
AS to tell which Sibling should be considered the "provider" and which the
"customer" in the context of a particular BGP update.

Thus, to reliably detect route leaks where the Propagation Path contains
adjacent Sibling ASes, we must consider the possibility of leaks arising within
a *sequence* of Transit ASes.

Based on the above logic, we may describe the verification procedure algorithm
as follows:

Given Propagation Path `P = [O, T1, T2, ..., Tn, R]` derived from a BGP update
`U`, originated at `O` and received at `R`, then:

-   If there exists **any** sequence of Transit ASes `[Ti, ..., Tj]` in `P`
    with `1 <= i <= j <= n` such that both:

    - `Ti` is Unauthorised by its Left Neighbor; and
    - `Tj` is Unauthorised by its Right Neighbor,

    then `U` has verification status **Invalid**;

-   Otherwise if for **all** sequences of Transit ASes `[Ti, ..., Tj]` in
    `P` with `1 <= i <= j <= n`:

    - `Ti` is Authorised by its Left Neighbor; or
    - `Tj` is Authorised by its Right Neighbor,

    then `U` has verification status **Valid**;

-   Otherwise, `U` has verification status **Unknown**.

## Formal Procedure

### Inputs

-   A BGP update with `AS_PATH` attribute **`as_path`**;
-   Receiver local ASN **`local_as`**; and
-   A complete set of all the ASPA objects published in the RPKI,
    **`aspa_set`**.

### Output

-   **`verification_status`**, having one of the following possible
    values:
    - `Unverifiable`
    - `Valid`
    - `Invalid`
    - `Unknown`

### Procedure

1.  Construct `propagation_path` from `as_path` and `local_as`:

    1.  Initialise `propagation_path` as an empty ordered sequence of 32-bit
        unsigned integers;

    2.  For each segment `as_segment` in `as_path`:

        1.  If `as_segment` has type other than `AS_SEQUENCE`, then halt with
            `validation_status =  Unverifiable`.

        2.  For each ASN `asn` appearing in `as_segment`, append `asn` to
            `propagation_path` if either:
            1. `propagation_path` is empty, or
            2. the last value in `propagation_path` is not equal to `asn`.

    3.  Append `local_as` to `propagation_path`.

    4.  Initialise `propagation_path_length` as an unsigned integer equal to
        the length of `propagation_path`.

2.  Initialise `partial_status` as `Valid`.

3.  We write `propagation_path[k]` to denote the `k-th` entry in
    `propagation_path`.

    For every pair of integers `i`, `j` such that
    `2 <= i <= j <= propagation_path_length - 1`:

    1.  Initialise `authorised_left` as an unordered set of 32-bit integers,
        equal to the union of all sets appearing in the SPAS field of objects
        in `aspa_set` where the CAS field is equal to `propagation_path[i-1]`

    2.  Initialise `authorised_right` as an unordered set of 32-bit integers,
        equal to the union of all sets appearing in the SPAS field of objects
        in `aspa_set` where the CAS field is equal to `propagation_path[j+1]`

    3.  If:

        1. Both `authorised_left` and `authorised_right` are non-empty; and
        2. `propagation_path[i]` is not a member of `authorised_left`; and
        3. `propagation_path[j]` is not a member of `authorised_right`,

        then halt with `validation_status = Invalid`.

    4.  If either:

        1. `propagation_path[i]` is a member of `authorised_left`; or
        2. `propagation_path[j]` is a member of `authorised_right`,

        then proceed to the next iteration of step 3.

    5.  Set `partial_status` status to `Unknown` and proceed to the next
        iteration of step 3.

4.  Halt with `validation_status = partial_status`
