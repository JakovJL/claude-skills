# Handoff to implementation

Carry the design into the project's actual tool rather than guessing a framework-specific skill name. An engineer needs:

- Objective, roles, exact workflow and expected business success.
- Confirmed API contract and authentication/session behavior.
- Participant/rate values, arrival model, ramp, duration, pauses and any synchronized-action window.
- Dataset, unique identities, expected saved records, cleanup and environment restrictions.
- Criteria, metrics, observation windows, stop and recovery conditions.
- Explicit proposals and unresolved inputs that must not silently become script defaults.

When implementation is part of the user's request, continue with the available engine and repository conventions. A missing skill is not a missing capability if ordinary tooling suffices. When only planning was requested, deliver the reviewable design and its remaining decisions.

Before interpreting a later run, compare achieved traffic with the design. A script that starts all users together can still submit them across a wide interval; a generator that drops arrivals did not deliver its configured profile. Record these differences before drawing capacity conclusions.
