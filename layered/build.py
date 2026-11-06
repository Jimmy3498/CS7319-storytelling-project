"""Build the Layered demo: python -m layered.build."""

from scripts.demo_bundle import BuildSpec, main

SPEC = BuildSpec(package="layered", label="Layered", port=8501)

if __name__ == "__main__":
    main(SPEC)
