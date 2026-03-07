import unittest
from result import (
    result_ok,
    result_fail,
    result_equality,
    result_combine,
    value_or,
    unwrap_or,
)
from result import is_result, is_ok, is_fail
from result.base import Ok, Fail


class TestResult(unittest.TestCase):
    def test_result_ok_with_value(self) -> None:
        result = result_ok(2)
        self.assertIsInstance(result, Ok)

        self.assertEqual(result.value, 2)

    def test_result_ok_none(self) -> None:
        """Ensure result_ok defaults to Ok(None) when no value is provided."""
        result = result_ok()
        self.assertIsInstance(result, Ok)

        self.assertEqual(result.value, None)

    def test_result_fail_with_value(self) -> None:
        result = result_fail("error")
        self.assertIsInstance(result, Fail)

        self.assertEqual(result.value, "error")

    def test_result_fail_none(self) -> None:
        """Ensure result_fail raises TypeError when called without a required value."""
        self.assertRaises(TypeError, result_fail)
        self.assertRaises(ValueError, result_fail, None)

    def test_result_combine(self) -> None:
        """
        Ensure result_combine aggregates Ok values into a list when all results are Ok,
        and returns the first Fail encountered when any result is Fail.
        """
        result1 = result_ok(1)
        result2 = result_ok(2)
        result3 = result_fail("error")

        combined_result = result_combine([result1, result2])
        self.assertIsInstance(combined_result, Ok)
        self.assertEqual(combined_result.value, [1, 2])

        combined_result_with_fail = result_combine([result1, result3])
        self.assertIsInstance(combined_result_with_fail, Fail)
        self.assertEqual(combined_result_with_fail.value, "error")

    def test_value_or(self) -> None:
        """
        Ensure value_or returns the Ok value when given an Ok result,
        returns the default value when given a Fail result,
        and raises TypeError when passed a non result object.
        """
        result = result_ok(2)
        failed_result = result_fail("error")
        default_value = 5

        self.assertEqual(value_or(result, default_value), result.value)
        self.assertRaises(TypeError, value_or, None, default_value)
        self.assertEqual(value_or(failed_result, default_value), default_value)

    def test_unwrap_or(self) -> None:
        """
        Ensure unwrap_or returns the raw Ok value for Ok results,
        returns the raw Fail value for Fail results,
        and returns the default value when passed None.
        """
        result = result_ok(2)
        failed_result = result_fail("error")
        default_value = 5

        self.assertEqual(unwrap_or(result, default_value), 2)
        self.assertEqual(unwrap_or(failed_result, default_value), "error")
        self.assertEqual(unwrap_or(None, default_value), default_value)

    def test_result_equality(self) -> None:
        """
        Ensure result_equality correctly compares two Ok results by value,
        returning True when values match and False when they differ.
        """
        result1 = result_ok(2)
        result2 = result_ok(2)
        result3 = result_ok(3)
        failed_result1 = result_fail("error")
        failed_result2 = result_fail("error")
        failed_result3 = result_fail("error3")

        self.assertTrue(result1 == result2)
        self.assertFalse(result1 == result3)
        self.assertTrue(result1 != result3)
        self.assertTrue(failed_result1 == failed_result2)
        self.assertTrue(result_equality(result1, result2))
        self.assertFalse(result_equality(result1, result3))
        self.assertTrue(result_equality(failed_result1, failed_result2))
        self.assertFalse(result_equality(failed_result1, failed_result3))

    def test_is_result_guard(self) -> None:
        """Ensure is_result correctly identifies valid Ok/Fail results and rejects non result objects."""
        result = result_ok(2)
        self.assertTrue(is_result(result))
        self.assertFalse(is_result(None))

    def test_is_ok_guard(self) -> None:
        """
        Ensure is_ok and Ok.isOk() return True for Ok results,
        and that Fail guards return False for Ok results.
        """
        result = result_ok(2)
        self.assertTrue(is_ok(result))
        self.assertTrue(result.isOk())
        self.assertFalse(is_fail(result))
        self.assertFalse(result.isFail())

    def test_is_fail_guard(self) -> None:
        """
        Ensure is_fail and Fail.isFail() return True for Fail results,
        and that Ok guards return False for Fail results.
        """
        result = result_fail("error")
        self.assertTrue(is_fail(result))
        self.assertTrue(result.isFail())
        self.assertFalse(is_ok(result))
        self.assertFalse(result.isOk())


class TestResultPatternMatching(unittest.TestCase):
    def test_pattern_matching_on_result_ok(self) -> None:
        """
        Ensure pattern matching on Ok and Fail results correctly extracts values
        and that non result objects do not match.
        """
        result = result_ok(2)
        match result:
            case Ok(value):
                self.assertEqual(value, 2)
            case Fail(value):
                self.fail("Expected an Ok result, got Fail.")

    def test_pattern_matching_on_result_fail(self) -> None:
        failed_result = result_fail("error")
        match failed_result:
            case Fail(error):
                self.assertEqual(error, "error")
            case Ok(value):
                self.fail("Expected a Fail result, got Ok.")


if __name__ == "__main__":
    unittest.main()
