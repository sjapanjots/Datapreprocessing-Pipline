"""Enable ``python -m data_pipeline`` to run the pipeline from a shell."""

from data_pipeline.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
