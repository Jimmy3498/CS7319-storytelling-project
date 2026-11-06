"""Build the Event-Based demo: python -m event_based.build."""

from scripts.demo_bundle import BuildSpec, main

SPEC = BuildSpec(package="event_based", label="Event-Based", port=8502)

if __name__ == "__main__":
    main(SPEC)
