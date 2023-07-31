Sample data gathered From an Enphase Envoy/Gateway using the `envoy.py` script
in the parent directory.  This data is from a site in the US with:

- Single phase service (split phase / standard US 120v/240v)
- Solar panels
- Batteries
- Generator
- Central US timezone

Timestamps appear to be in Unix format (seconds since midnight Jan 1, 1970).

This data was dumped at night, so much of the production information is 0.

Some data has been redacted as I'm unsure what is considered "private" in the
Enphase world.  Where it has, you will find "REDACTED-\<description\>".  Some data
is tracked through its redactions.  For example, a file with:

    [
        {
            "some_secret_number": 12345,
            "another_secret_number": 67890
        }
    ]

Would be updated to:

    [
        {
            "some_secret_number": REDACTED-5-DIGIT-INTEGER-A,
            "another_secret_number": REDACTED-5-DIGIT-INTEGER-B
        }
    ]

Note the lack of quotes (rendering the JSON invalid) because it was an integer
and that the use of "A" and "B" in the name to indicate that they were
different values.  Nested values may have "AA", "AB", "AC"... to indicate three
unique values nested under previously redacted value "A".
