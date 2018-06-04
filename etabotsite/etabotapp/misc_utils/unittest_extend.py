"""Additional Assertion functions for unit tests."""


def assertFileEqual(target_filename, reference_filename, unittest_instance):
    """Return None. Raises unittest assertion error if files are not equal."""
    with open(target_filename) as f:
        target = f.readlines()

    with open(reference_filename) as f:
        reference = f.readlines()

    unittest_instance.assertEqual(reference, target)
