# Dev Tools (Legacy)

This folder collects legacy utilities that referenced deferred-amortization fields.
The old Tkinter code generator previously shipped in `setup.py` lives only in git
history. The current application uses the multi-CUIT DuckDB backend and historical
value model only, so please do not run the generator. If you really need to revisit
that prototype, checkout a commit prior to the multi-company migration.
